
import logging
import math
import Math
import BigWorld
from debug_utils import LOG_CURRENT_EXCEPTION
from Avatar import PlayerAvatar
from gun_rotation_shared import decodeGunAngles

from mod_constants import MOD
from hook import overrideMethod

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


class StatsCollector(object):
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
        #vehicle = avatar.vehicle
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

g_statscollector = StatsCollector()
