
import math
import Math
import BigWorld
from Avatar import PlayerAvatar
from gun_rotation_shared import decodeGunAngles

from constants import MOD_NAME
from events import overrideMethod

g_dispersionStats = None


@overrideMethod(PlayerAvatar, 'getOwnVehicleShotDispersionAngle')
def playerAvatar_getOwnVehicleShotDispersionAngle(orig, self, turretRotationSpeed, withShot = 0):
    dispersionAngle = result = orig(self, turretRotationSpeed, withShot)
    if g_dispersionStats:
        avatar = self
        g_dispersionStats.currTime = BigWorld.time()
        try:
            g_dispersionStats._updateDispersionAngle(avatar, dispersionAngle, turretRotationSpeed, withShot)
        except:
            BigWorld.logWarning(MOD_NAME, 'fail to _updateDispersionAngle', None)
        try:
            g_dispersionStats._updateAimingInfo(avatar)
        except:
            BigWorld.logWarning(MOD_NAME, 'fail to _updateAimingInfo', None)
        try:
            g_dispersionStats._updateVehicleSpeeds(avatar)
        except:
            BigWorld.logWarning(MOD_NAME, 'fail to _updateVehicleSpeeds', None)
        try:
            g_dispersionStats._updateVehicleEngineState(avatar)
        except:
            BigWorld.logWarning(MOD_NAME, 'fail to _updateVehicleEngineState', None)
        try:
            g_dispersionStats._updateGunAngles(avatar)
        except:
            BigWorld.logWarning(MOD_NAME, 'fail to _updateGunAngles', None)
        try:
            g_dispersionStats._updateVehicleDirection(avatar)
        except:
            BigWorld.logWarning(MOD_NAME, 'fail to _updateVehicleDirection', None)
        return result


class DispersionStats(object):
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
        self.vehicleRYaw = self.vehicleYaw - cameraDirection.yaw

    def _updateGunAngles(self, avatar):
        vehicle = avatar.vehicle
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
        detailedEngineState = avatar.vehicle.appearance._CompoundAppearance__detailedEngineState
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

g_dispersionStats = DispersionStats()
