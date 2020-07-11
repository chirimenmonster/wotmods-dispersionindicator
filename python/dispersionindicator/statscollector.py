
import logging
import math
import Math
import BigWorld
import BattleReplay
from Event import Event
from debug_utils import LOG_CURRENT_EXCEPTION
from Avatar import PlayerAvatar
from AvatarInputHandler.control_modes import _GunControlMode
from AvatarInputHandler.gun_marker_ctrl import _CrosshairShotResults
from gun_rotation_shared import decodeGunAngles
from vehicle_extras import ShowShooting
from gui.battle_control import avatar_getter
from gui.battle_control.controllers.crosshair_proxy import CrosshairDataProxy
from material_kinds import EFFECT_MATERIAL_INDEXES_BY_IDS, EFFECT_MATERIAL_NAMES_BY_INDEXES, IDS_BY_NAMES


from mod_constants import MOD, EVENT, CLIENT_STATUS_LIST
from hook import overrideMethod, overrideClassMethod

_logger = logging.getLogger(MOD.NAME)

g_statscollector = None

def callOriginal(prev=False):
    def decorator(func):
        def wrapper(orig, *args, **kwargs):
            result = None
            if prev:
                result = orig(*args, **kwargs)
            try:
                _ = func(result, *args, **kwargs)
            except:
                LOG_CURRENT_EXCEPTION()
            if not prev:
                result = orig(*args, **kwargs)
            return result
        return wrapper
    return decorator


@overrideMethod(PlayerAvatar, 'getOwnVehicleShotDispersionAngle')
@callOriginal(prev=True)
def playerAvatar_getOwnVehicleShotDispersionAngle(orig_result, self, turretRotationSpeed, withShot = 0):
    dispersionAngle = orig_result
    avatar = self
    collector = g_statsCollector
    collector.updatePing()
    collector.updateDispersionAngle(avatar, dispersionAngle, turretRotationSpeed, withShot)
    collector.updateAimingInfo(avatar)
    collector.updateVehicleSpeeds(avatar)
    collector.updateVehicleEngineState(avatar)
    collector.updateGunAngles(avatar)
    collector.updateVehicleDirection(avatar)


@overrideMethod(_GunControlMode, 'updateGunMarker')
@callOriginal(prev=True)
def gunControlMode_updateGunMarker(orig_result, self, markerType, pos, direction, size, relaxTime, collData):
    avatar = BigWorld.player()
    g_statsCollector.updateShotInfo(avatar, pos)


@overrideMethod(PlayerAvatar, 'shoot')
@callOriginal(prev=False)
def playerAvatar_shoot(_, self, isRepeat = False):
    if not self._PlayerAvatar__isOnArena:
        return
    else:
        dualGunControl = self.inputHandler.dualGunControl
        if dualGunControl is not None and dualGunControl.isShotLocked:
            return
        if self._PlayerAvatar__tryChargeCallbackID is not None:
            return
        for deviceName, stateName in self._PlayerAvatar__deviceStates.iteritems():
            msgName = self._PlayerAvatar__cantShootCriticals.get(deviceName + '_' + stateName)
            if msgName is not None:
                return
        canShoot, error = self.guiSessionProvider.shared.ammo.canShoot(isRepeat)
        if not canShoot:
            return
        if self._PlayerAvatar__gunReloadCommandWaitEndTime > BigWorld.time():
            return
        if self._PlayerAvatar__shotWaitingTimerID is not None or self._PlayerAvatar__isWaitingForShot:
            return
        if self._PlayerAvatar__chargeWaitingTimerID is not None:
            return
        if self.isGunLocked or self._PlayerAvatar__isOwnBarrelUnderWater():
            return
        if self._PlayerAvatar__isOwnVehicleSwitchingSiegeMode():
            return
    time = BigWorld.time()
    _logger.debug('catch PlayerAvatar.shoot: time={}'.format(time))
    g_statsCollector.onEvent(EVENT.ACTION_SHOOT)


@overrideMethod(PlayerAvatar, 'showShotResults')
@callOriginal(prev=False)
def playerAvatar_showShotResults(_, self, result):
    time = BigWorld.time()
    _logger.debug('catch PlayerAvatar.showShotResults: time={}'.format(time))
    g_statsCollector.onEvent(EVENT.RECEIVE_SHOT_RESULT)


@overrideMethod(ShowShooting, '_ShowShooting__doShot')
@callOriginal(prev=False)
def showShooting_doShot(_, self, data):
    if not data['entity'].isPlayerVehicle:
        return
    time = BigWorld.time()
    _logger.debug('catch ShowShooting.__doShot: time={}'.format(time))
    g_statsCollector.onEvent(EVENT.RECEIVE_SHOT)


@overrideMethod(CrosshairDataProxy, '_CrosshairDataProxy__setGunMarkerState')
@callOriginal(prev=True)
def crosshairDataProxy_setGunMarkerState(orig_result, self, markerType, value):
    excludeTeam = 0
    hitPoint, direction, collision = value
    resultPenetrationInfo = {}
    piercingPercent = None
    for _ in [0]:
        #
        # from AvatarInputHandler.gun_marker_ctrl._CrosshairShotResults.getShotResult
        if collision is None:
            break
        entity = collision.entity
        if entity.__class__.__name__ not in ('Vehicle', 'DestructibleEntity'):
            break
        if entity.health <= 0 or entity.publicInfo['team'] == excludeTeam:
            break
        resultPenetrationInfo['entityType'] = entity.__class__.__name__
        resultPenetrationInfo['entityName'] = entity.typeDescriptor.type.name if entity.__class__.__name__ == 'Vehicle' else None
        player = BigWorld.player()
        if player is None:
            break
        vDesc = player.getVehicleDescriptor()
        shell = vDesc.shot.shell
        caliber = shell.caliber
        shellKind = shell.kind
        ppDesc = vDesc.shot.piercingPower
        maxDist = vDesc.shot.maxDistance
        dist = (hitPoint - player.getOwnVehiclePosition()).length
        piercingPower = _CrosshairShotResults._computePiercingPowerAtDist(ppDesc, dist, maxDist)
        fullPiercingPower = piercingPower
        minPP, maxPP = _CrosshairShotResults._computePiercingPowerRandomization(shell)
        isJet = False
        jetStartDist = None
        ignoredMaterials = set()
        collisionsDetails = _CrosshairShotResults._getAllCollisionDetails(hitPoint, direction, entity)
        if collisionsDetails is None:
            break
        for cDetails in collisionsDetails:
            try:
                mat_kind = cDetails.matInfo.kind
                mat_name = None
                for k, v in IDS_BY_NAMES.items():
                    if v == mat_kind:
                        mat_name = k
                        break
                _logger.info('entity={}, kind={} ({}), armor={}'.format(resultPenetrationInfo['entityName'], mat_kind, mat_name, cDetails.matInfo.armor))
            except:
                LOG_CURRENT_EXCEPTION()
            if isJet:
                jetDist = cDetails.dist - jetStartDist
                if jetDist > 0.0:
                    piercingPower *= 1.0 - jetDist * _CrosshairShotResults._SHELL_EXTRA_DATA[shellKind].jetLossPPByDist
            if cDetails.matInfo is None:
                piercingPercent = None
            else:
                matInfo = cDetails.matInfo
                if (cDetails.compName, matInfo.kind) in ignoredMaterials:
                    continue
                hitAngleCos = cDetails.hitAngleCos if matInfo.useHitAngle else 1.0
                if resultPenetrationInfo.get('firstArmor', None) is None:
                    resultPenetrationInfo['firstArmor'] = {
                        'hitAngleCos': hitAngleCos,
                        'armor': matInfo.armor,
                        'penetrationArmor': _CrosshairShotResults._computePenetrationArmor(shell.kind, hitAngleCos, matInfo, shell.caliber)
                    }
                if not isJet and _CrosshairShotResults._shouldRicochet(shellKind, hitAngleCos, matInfo, caliber):
                    break
                piercingPercent = 1000.0
                if piercingPower > 0.0:
                    penetrationArmor = _CrosshairShotResults._computePenetrationArmor(shellKind, hitAngleCos, matInfo, caliber)
                    piercingPercent = 100.0 + (penetrationArmor - piercingPower) / fullPiercingPower * 100.0
                    piercingPower -= penetrationArmor
                if matInfo.vehicleDamageFactor:
                    break
                elif matInfo.extra:
                    piercingPercent = None
                if matInfo.collideOnceOnly:
                    ignoredMaterials.add((cDetails.compName, matInfo.kind))
            if piercingPower <= 0.0:
                break
            if _CrosshairShotResults._SHELL_EXTRA_DATA[shellKind].jetLossPPByDist > 0.0:
                isJet = True
                mInfo = cDetails.matInfo
                armor = mInfo.armor if mInfo is not None else 0.0
                jetStartDist = cDetails.dist + armor * 0.001                

    g_statsCollector.updatePenetrationArmor(piercingPercent, resultPenetrationInfo)


class ClientStatus(object):
    __slots__ = CLIENT_STATUS_LIST

    @property
    def aimingFactor(self):
        return self.dAngleAiming / self.shotDispersionAngle

    @property
    def aimingTimeConverging(self):
        factor = self.aimingStartFactor / self.multFactor
        return self.aimingStartTime - self.currTime + self.aimingTime * math.log(factor)

    @property
    def modifiedAimingFactor(self):
        return self.aimingFactor / self.multFactor

    @property
    def scoreDispersion(self):
        k = 1.0
        fm = 16.0
        fc = self.modifiedAimingFactor
        return (fc ** k - 1.0) / (fm ** k - 1.0) * 100.0

    @property
    def flightTime(self):
        return self.shotDistanceH / self.shotSpeedH


class StatsCollector(object):
    def __init__(self):
        self.eventHandlers = Event()

    def onEvent(self, reason):
        self.eventHandlers(reason)

    def updateArenaInfo(self):
        stats = g_clientStatus
        stats.arenaName = avatar_getter.getArena().arenaType.geometryName
        stats.vehicleName = avatar_getter.getVehicleTypeDescriptor().type.name

    def updatePing(self):
        replayCtrl = BattleReplay.g_replayCtrl
        stats = g_clientStatus
        stats.currTime = BigWorld.time()
        if replayCtrl.isPlaying:
            ping = replayCtrl.ping
            fps = BigWorld.getFPS()[1]
            fpsReplay = int(replayCtrl.fps)
        else:
            ping = BigWorld.statPing()
            fps = BigWorld.getFPS()[1]
            fpsReplay = -1
        try:
            stats.ping = int(ping)
            stats.fps = int(fps)
        except (ValueError, OverflowError):
            stats.ping = -1
            stats.fps = -1
        stats.fpsReplay = fpsReplay
        latency = BigWorld.LatencyInfo().value
        stats.latency_0 = latency[0]
        stats.latency_1 = latency[1]
        stats.latency_2 = latency[2]
        stats.latency_3 = latency[3]

    def updateDispersionAngle(self, avatar, dispersionAngle, turretRotationSpeed, withShot):
        stats = g_clientStatus
        stats.dAngleAiming = dispersionAngle[0]
        stats.dAngleIdeal = dispersionAngle[1]
        stats.turretRotationSpeed = turretRotationSpeed
        vDescr = avatar._PlayerAvatar__getDetailedVehicleDescriptor()
        stats.additiveFactor = avatar._PlayerAvatar__getAdditiveShotDispersionFactor(vDescr)
        stats.shotDispersionAngle = vDescr.gun.shotDispersionAngle
        if withShot == 0:
            stats.shotFactor = 0.0
        elif withShot == 1:
            stats.shotFactor = vDescr.gun.shotDispersionFactors['afterShot']
        else:
            stats.shotFactor = vDescr.gun.shotDispersionFactors['afterShotInBurst']

    def updateAimingInfo(self, avatar):
        stats = g_clientStatus
        aimingInfo = avatar._PlayerAvatar__aimingInfo
        stats.aimingStartTime = aimingInfo[0]
        stats.aimingStartFactor = aimingInfo[1]
        stats.multFactor = aimingInfo[2]
        stats.factorsTurretRotation = aimingInfo[3]
        stats.factorsMovement = aimingInfo[4]
        stats.factorsRotation = aimingInfo[5]
        stats.aimingTime = aimingInfo[6]

    def updateVehicleDirection(self, avatar):
        stats = g_clientStatus
        matrix = Math.Matrix(avatar.getOwnVehicleMatrix())
        stats.vehicleYaw = matrix.yaw
        stats.vehiclePitch = matrix.pitch
        stats.vehicleRoll = matrix.roll
        camera = BigWorld.camera()
        cameraDirection = camera.direction
        rYaw = stats.vehicleYaw - cameraDirection.yaw
        if rYaw > math.pi:
            rYaw -= math.pi * 2
        elif rYaw < -math.pi:
            rYaw += math.pi * 2
        stats.vehicleRYaw = rYaw

    def updateGunAngles(self, avatar):
        stats = g_clientStatus
        vehicle = avatar.getVehicleAttached()
        vd = vehicle.typeDescriptor
        #gunOffs = vd.turret.gunPosition
        #turretOffs = vd.hull.turretPositions[0] + vd.chassis.hullPosition
        turretYaw, gunPitch = decodeGunAngles(vehicle.gunAnglesPacked, vd.gun.pitchLimits['absolute'])
        stats.turretYaw = turretYaw
        stats.gunPitch = gunPitch

    def updateVehicleSpeeds(self, avatar):
        stats = g_clientStatus
        vehicleSpeed, vehicleRSpeed = avatar.getOwnVehicleSpeeds(True)
        stats.vehicleSpeed = vehicleSpeed
        stats.vehicleRSpeed = vehicleRSpeed

    def updateVehicleEngineState(self, avatar):
        stats = g_clientStatus
        vehicle = avatar.getVehicleAttached()
        detailedEngineState = vehicle.appearance.detailedEngineState
        stats.engineRPM = detailedEngineState.rpm
        stats.engineRelativeRPM = detailedEngineState.relativeRPM

    def updateShotInfo(self, avatar, hitPoint):
        stats = g_clientStatus
        shotDescr = avatar.getVehicleDescriptor().shot
        stats.shotSpeed = shotDescr.speed
        stats.shotGravity = shotDescr.gravity
        shotPos, shotVec = avatar.gunRotator.getCurShotPosition()
        stats.shotSpeedH = shotVec.flatDistTo(Math.Vector3((0.0, 0.0, 0.0)))
        stats.shotSpeedV = shotVec.y
        stats.shotPosX = shotPos.x
        stats.shotPosY = shotPos.y
        stats.shotPosZ = shotPos.z
        shotDistance = hitPoint - shotPos
        stats.shotDistance = shotDistance.length
        stats.shotDistanceH = shotPos.flatDistTo(hitPoint)
        stats.shotDistanceV = shotDistance.y
        position = avatar.getOwnVehiclePosition()
        distance = hitPoint - position
        stats.distance = distance.length
        stats.distanceH = position.flatDistTo(hitPoint)
        stats.distanceV = distance.y
        stats.vehiclePosX = position.x
        stats.vehiclePosY = position.y
        stats.vehiclePosZ = position.z
        stats.targetPosX = hitPoint.x
        stats.targetPosY = hitPoint.y
        stats.targetPosZ = hitPoint.z

    def updatePenetrationArmor(self, piercingPercent, penetrationInfo):
        stats = g_clientStatus
        stats.piercingPercent = piercingPercent
        if 'firstArmor' in penetrationInfo:
            stats.hitAngleCos = penetrationInfo['firstArmor']['hitAngleCos']
            stats.penetrationArmor = penetrationInfo['firstArmor']['penetrationArmor']
            stats.armor = penetrationInfo['firstArmor']['armor']
            stats.entityName = penetrationInfo['entityName']
        else:
            stats.hitAngleCos = None
            stats.penetrationArmor = None
            stats.armor = None
            stats.entityName = None


g_statsCollector = StatsCollector()
g_clientStatus = ClientStatus()
