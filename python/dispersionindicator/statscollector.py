
import logging
import math
import Math
import BigWorld
import BattleReplay
from Event import Event
from debug_utils import LOG_CURRENT_EXCEPTION
from Avatar import PlayerAvatar
from AvatarInputHandler.control_modes import _GunControlMode
from gun_rotation_shared import decodeGunAngles
from vehicle_extras import ShowShooting

from mod_constants import MOD, EVENT
from hook import overrideMethod, overrideClassMethod

_logger = logging.getLogger(MOD.NAME)

g_statscollector = None



@overrideMethod(PlayerAvatar, 'getOwnVehicleShotDispersionAngle')
def playerAvatar_getOwnVehicleShotDispersionAngle(orig, self, turretRotationSpeed, withShot = 0):
    dispersionAngle = result = orig(self, turretRotationSpeed, withShot)
    if g_statscollector:
        avatar = self
        collector = g_statscollector
        collector.currTime = BigWorld.time()
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
    _logger.info('catch PlayerAvatar.shoot: time={}'.format(time))
    g_statscollector.onEvent(EVENT.ACTION_SHOOT)


def hook_playerAvatar_showShotResults(self, result):
    time = BigWorld.time()
    _logger.info('catch PlayerAvatar.showShotResults: time={}'.format(time))
    g_statscollector.onEvent(EVENT.RECEIVE_SHOT_RESULT)


def hook_showShooting_doShot(self, data):
    if not data['entity'].isPlayerVehicle:
        return
    time = BigWorld.time()
    _logger.info('catch ShowShooting.__doShot: time={}'.format(time))
    g_statscollector.onEvent(EVENT.RECEIVE_SHOT)


class StatsCollector(object):
    def __init__(self):
        self.eventHandlers = Event()

    def _updatePing(self):
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying:
            ping = replayCtrl.ping
            fps = BigWorld.getFPS()[1]
            self.fpsReplay = int(replayCtrl.fps)
        else:
            ping = BigWorld.statPing()
            fps = BigWorld.getFPS()[1]
            self.fpsReplay = -1
        try:
            self.ping = int(ping)
            self.fps = int(fps)
        except (ValueError, OverflowError):
            self.ping = -1
            self.fps = -1
        latency = BigWorld.LatencyInfo().value
        self.latency_0 = latency[0]
        self.latency_1 = latency[1]
        self.latency_2 = latency[2]
        self.latency_3 = latency[3]

    def _updateDispersionAngle(self, avatar, dispersionAngle, turretRotationSpeed, withShot):
        self.dAngleAiming = dispersionAngle[0]
        self.dAngleIdeal = dispersionAngle[1]
        self.turretRotationSpeed = turretRotationSpeed
        vDescr = avatar._PlayerAvatar__getDetailedVehicleDescriptor()
        self.additiveFactor = avatar._PlayerAvatar__getAdditiveShotDispersionFactor(vDescr)
        self.shotDispersionAngle = vDescr.gun.shotDispersionAngle
        if withShot == 0:
            self.shotFactor = 0.0
        elif withShot == 1:
            self.shotFactor = vDescr.gun.shotDispersionFactors['afterShot']
        else:
            self.shotFactor = vDescr.gun.shotDispersionFactors['afterShotInBurst']

    def _updateAimingInfo(self, avatar):
        aimingInfo = avatar._PlayerAvatar__aimingInfo
        self.aimingStartTime = aimingInfo[0]
        self.aimingStartFactor = aimingInfo[1]
        self.multFactor = aimingInfo[2]
        self.factorsTurretRotation = aimingInfo[3]
        self.factorsMovement = aimingInfo[4]
        self.factorsRotation = aimingInfo[5]
        self.aimingTime = aimingInfo[6]

    def _updateVehicleDirection(self, avatar):
        matrix = Math.Matrix(avatar.getOwnVehicleMatrix())
        self.vehicleYaw = matrix.yaw
        self.vehiclePitch = matrix.pitch
        self.vehicleRoll = matrix.roll
        camera = BigWorld.camera()
        cameraDirection = camera.direction
        rYaw = self.vehicleYaw - cameraDirection.yaw
        if rYaw > math.pi:
            rYaw -= math.pi * 2
        elif rYaw < -math.pi:
            rYaw += math.pi * 2
        self.vehicleRYaw = rYaw

    def _updateGunAngles(self, avatar):
        vehicle = avatar.getVehicleAttached()
        vd = vehicle.typeDescriptor
        #gunOffs = vd.turret.gunPosition
        #turretOffs = vd.hull.turretPositions[0] + vd.chassis.hullPosition
        turretYaw, gunPitch = decodeGunAngles(vehicle.gunAnglesPacked, vd.gun.pitchLimits['absolute'])
        self.turretYaw = turretYaw
        self.gunPitch = gunPitch

    def _updateVehicleSpeeds(self, avatar):
        vehicleSpeed, vehicleRSpeed = avatar.getOwnVehicleSpeeds(True)
        self.vehicleSpeed = vehicleSpeed
        self.vehicleRSpeed = vehicleRSpeed

    def _updateVehicleEngineState(self, avatar):
        vehicle = avatar.getVehicleAttached()
        detailedEngineState = vehicle.appearance.detailedEngineState
        self.engineRPM = detailedEngineState.rpm
        self.engineRelativeRPM = detailedEngineState.relativeRPM

    def _updateShotInfo(self, avatar, hitPoint):
        shotDescr = avatar.getVehicleDescriptor().shot
        self.shotSpeed = shotDescr.speed
        self.shotGravity = shotDescr.gravity
        shotPos, shotVec = avatar.gunRotator.getCurShotPosition()
        self.shotSpeedH = shotVec.flatDistTo(Math.Vector3((0.0, 0.0, 0.0)))
        self.shotSpeedV = shotVec.y
        self.shotPosX = shotPos.x
        self.shotPosY = shotPos.y
        self.shotPosZ = shotPos.z
        shotDistance = hitPoint - shotPos
        self.shotDistance = shotDistance.length
        self.shotDistanceH = shotPos.flatDistTo(hitPoint)
        self.shotDistanceV = shotDistance.y
        position = avatar.getOwnVehiclePosition()
        distance = hitPoint - position
        self.distance = distance.length
        self.distanceH = position.flatDistTo(hitPoint)
        self.distanceV = distance.y
        self.vehiclePosX = position.x
        self.vehiclePosY = position.y
        self.vehiclePosZ = position.z
        self.targetPosX = hitPoint.x
        self.targetPosY = hitPoint.y
        self.targetPosZ = hitPoint.z

    def onEvent(self, reason):
        self.eventHandlers(reason)

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


g_statscollector = StatsCollector()
