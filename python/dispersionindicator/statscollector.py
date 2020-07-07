
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

from mod_constants import MOD, EVENT, CLIENT_STATUS_LIST
from hook import overrideMethod, overrideClassMethod

_logger = logging.getLogger(MOD.NAME)

g_statscollector = None


@overrideMethod(PlayerAvatar, 'getOwnVehicleShotDispersionAngle')
def playerAvatar_getOwnVehicleShotDispersionAngle(orig, self, turretRotationSpeed, withShot = 0):
    dispersionAngle = result = orig(self, turretRotationSpeed, withShot)
    if g_statscollector:
        avatar = self
        collector = g_statscollector
        try:
            collector._updatePing()
        except:
            LOG_CURRENT_EXCEPTION()
            _logger.warning('fail to _updatePing')
        try:
            collector._updateDispersionAngle(avatar, dispersionAngle, turretRotationSpeed, withShot)
        except:
            LOG_CURRENT_EXCEPTION()
            _logger.warning('fail to _updateDispersionAngle')
        try:
            collector._updateAimingInfo(avatar)
        except:
            LOG_CURRENT_EXCEPTION()
            _logger.warning('fail to _updateAimingInfo')
        try:
            collector._updateVehicleSpeeds(avatar)
        except:
            LOG_CURRENT_EXCEPTION()
            _logger.warning('fail to _updateVehicleSpeeds')
        try:
            collector._updateVehicleEngineState(avatar)
        except:
            LOG_CURRENT_EXCEPTION()
            _logger.warning('fail to _updateVehicleEngineState')
        try:
            collector._updateGunAngles(avatar)
        except:
            LOG_CURRENT_EXCEPTION()
            _logger.warning('fail to _updateGunAngles')
        try:
            collector._updateVehicleDirection(avatar)
        except:
            LOG_CURRENT_EXCEPTION()
            _logger.warning('fail to _updateVehicleDirection')
        return result

@overrideMethod(PlayerAvatar, 'shoot')
def playerAvatar_shoot(orig, *args, **kwargs):
    try:
        hook_playerAvatar_shoot(*args, **kwargs)
    except:
        LOG_CURRENT_EXCEPTION()
        _logger.warning('failed to call hook_playerAvatar_shoot')
    return orig(*args, **kwargs)


@overrideMethod(PlayerAvatar, 'showShotResults')
def playerAvatar_showShotResults(orig, *args, **kwargs):
    try:
        hook_playerAvatar_showShotResults(*args, **kwargs)
    except:
        LOG_CURRENT_EXCEPTION()
        _logger.warning('failed to call hook_playerAvatar_showShotResult')
    return orig(*args, **kwargs)


@overrideMethod(ShowShooting, '_ShowShooting__doShot')
def showShooting_doShot(orig, *args, **kwargs):
    try:
        hook_showShooting_doShot(*args, **kwargs)
    except:
        LOG_CURRENT_EXCEPTION()
        _logger.warning('failed to call hook_showShooting_doShot')
    return orig(*args, **kwargs)


@overrideMethod(_GunControlMode, 'updateGunMarker')
def gunControlMode_updateGunMarker(orig, self, markerType, pos, direction, size, relaxTime, collData):
    result = orig(self, markerType, pos, direction, size, relaxTime, collData)
    avatar = BigWorld.player()
    collector = g_statscollector
    try:
        collector._updateShotInfo(avatar, pos)
    except:
        LOG_CURRENT_EXCEPTION()
        _logger.warning('fail to _updateShotInfo')
    return result


@overrideMethod(CrosshairDataProxy, '_CrosshairDataProxy__setGunMarkerState')
def _CrosshairDataProxy_setGunMarkerState(orig, *args, **kwargs):
    result = orig(*args, **kwargs)
    try:
        hook_crosshairDataProxy_setGunMarkerState(*args, **kwargs)
    except:
        LOG_CURRENT_EXCEPTION()
        _logger.warning('failed to call hook_crosshairDataProxy_setGunMarkerState')
    return result


def hook_playerAvatar_shoot(self, isRepeat = False):
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
    g_statscollector.onEvent(EVENT.ACTION_SHOOT)


def hook_playerAvatar_showShotResults(self, result):
    time = BigWorld.time()
    _logger.debug('catch PlayerAvatar.showShotResults: time={}'.format(time))
    g_statscollector.onEvent(EVENT.RECEIVE_SHOT_RESULT)


def hook_showShooting_doShot(self, data):
    if not data['entity'].isPlayerVehicle:
        return
    time = BigWorld.time()
    _logger.debug('catch ShowShooting.__doShot: time={}'.format(time))
    g_statscollector.onEvent(EVENT.RECEIVE_SHOT)


def hook_crosshairDataProxy_setGunMarkerState(self, markerType, value):
    hitPoint, direction, collision = value
    armor, hitAngleCos, penetrationArmor = None, None, None
    for _ in [0]:
        if collision is None:
            break
        player = BigWorld.player()
        if player is None:
            break
        vDesc = player.getVehicleDescriptor()
        shell = vDesc.shot.shell
        entity = collision.entity
        collisionsDetails = _CrosshairShotResults._getAllCollisionDetails(hitPoint, direction, entity)
        if collisionsDetails is None:
            break
        for cDetails in collisionsDetails:
            if cDetails.matInfo is None:
                continue
            matInfo = cDetails.matInfo
            hitAngleCos = cDetails.hitAngleCos if matInfo.useHitAngle else 1.0
            armor = matInfo.armor
            penetrationArmor = _CrosshairShotResults._computePenetrationArmor(shell.kind, hitAngleCos, matInfo, shell.caliber)
            break
    g_statscollector.updatePenetrationArmor(penetrationArmor, armor, hitAngleCos)


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

    def _updatePing(self):
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

    def _updateDispersionAngle(self, avatar, dispersionAngle, turretRotationSpeed, withShot):
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

    def _updateAimingInfo(self, avatar):
        stats = g_clientStatus
        aimingInfo = avatar._PlayerAvatar__aimingInfo
        stats.aimingStartTime = aimingInfo[0]
        stats.aimingStartFactor = aimingInfo[1]
        stats.multFactor = aimingInfo[2]
        stats.factorsTurretRotation = aimingInfo[3]
        stats.factorsMovement = aimingInfo[4]
        stats.factorsRotation = aimingInfo[5]
        stats.aimingTime = aimingInfo[6]

    def _updateVehicleDirection(self, avatar):
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

    def _updateGunAngles(self, avatar):
        stats = g_clientStatus
        vehicle = avatar.getVehicleAttached()
        vd = vehicle.typeDescriptor
        #gunOffs = vd.turret.gunPosition
        #turretOffs = vd.hull.turretPositions[0] + vd.chassis.hullPosition
        turretYaw, gunPitch = decodeGunAngles(vehicle.gunAnglesPacked, vd.gun.pitchLimits['absolute'])
        stats.turretYaw = turretYaw
        stats.gunPitch = gunPitch

    def _updateVehicleSpeeds(self, avatar):
        stats = g_clientStatus
        vehicleSpeed, vehicleRSpeed = avatar.getOwnVehicleSpeeds(True)
        stats.vehicleSpeed = vehicleSpeed
        stats.vehicleRSpeed = vehicleRSpeed

    def _updateVehicleEngineState(self, avatar):
        stats = g_clientStatus
        vehicle = avatar.getVehicleAttached()
        detailedEngineState = vehicle.appearance.detailedEngineState
        stats.engineRPM = detailedEngineState.rpm
        stats.engineRelativeRPM = detailedEngineState.relativeRPM

    def _updateShotInfo(self, avatar, hitPoint):
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

    def updatePenetrationArmor(self, penetrationArmor, armor, hitAngleCos):
        stats = g_clientStatus
        stats.penetrationArmor = penetrationArmor
        stats.armor = armor
        stats.hitAngleCos = hitAngleCos


g_statscollector = StatsCollector()
g_clientStatus = ClientStatus()
