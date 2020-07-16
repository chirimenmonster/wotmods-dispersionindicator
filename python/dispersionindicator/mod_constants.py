
import math

from constants import ARENA_PERIOD
from gui.battle_control.battle_constants import CROSSHAIR_VIEW_ID
from skeletons.gui.app_loader import GuiGlobalSpaceID

class MOD:
    ID = '${mod_id}'
    PACKAGE_ID = '${package_id}'
    NAME = '${name}'
    VERSION = '${version}'

CONFIG_FILES = [
    '${resource_dir}/default.json',
    '${resource_dir}/config.json',
    '${config_file}'
]

LOG_DIR = '${log_dir}'
LOG_FILE = '${log_file}'

CONSTANT = {
    'MS_TO_KMH':    3600.0 / 1000.0,
    'RAD_TO_DEG':   180.0 / math.pi
}

CROSSHAIR_VIEW_SYMBOL = {
    CROSSHAIR_VIEW_ID.UNDEFINED:    'UNDEFINED',
    CROSSHAIR_VIEW_ID.ARCADE:       'ARCADE',
    CROSSHAIR_VIEW_ID.SNIPER:       'SNIPER',
    CROSSHAIR_VIEW_ID.STRATEGIC:    'STRATEGIC',
    CROSSHAIR_VIEW_ID.POSTMORTEM:   'POSTMORTEM'
}

ARENA_PERIOD_SYMBOL = {
    ARENA_PERIOD.IDLE:          'IDLE',
    ARENA_PERIOD.WAITING :      'WAITING',
    ARENA_PERIOD.PREBATTLE:     'PREBATTLE',
    ARENA_PERIOD.BATTLE:        'BATTLE',
    ARENA_PERIOD.AFTERBATTLE:   'AFTERBATTLE'
}

GUI_GLOBAL_SPACE_SYMBOL = {
    GuiGlobalSpaceID.UNDEFINED:         'UNDEFINED',
    GuiGlobalSpaceID.WAITING:           'WAITING',
    GuiGlobalSpaceID.INTRO_VIDEO:       'INTRO_VIDEO',
    GuiGlobalSpaceID.LOGIN:             'LOGIN',
    GuiGlobalSpaceID.LOBBY:             'LOBBY',
    GuiGlobalSpaceID.BATTLE_LOADING:    'BATTLE_LOADING',
    GuiGlobalSpaceID.BATTLE:            'BATTLE',
}

class EVENT:
    ACTION_SHOOT = 'actionShoot'
    RECEIVE_SHOT = 'receiveShot'
    RECEIVE_SHOT_RESULT = 'receiveShotResult'
    UPDATE_PENETRATION_ARMOR = 'updatePenetrationArmor'
    UPDATE_DISPERSION_ANGLE = 'updateDispersionAngle'

EVENT_LIST = [
    EVENT.ACTION_SHOOT,
    EVENT.RECEIVE_SHOT,
    EVENT.RECEIVE_SHOT_RESULT,
    EVENT.UPDATE_PENETRATION_ARMOR,
    EVENT.UPDATE_DISPERSION_ANGLE
]

CLIENT_STATUS_LIST = [
    'localDateTime', 'currTime', 'eventTime', 'eventName', 'arenaName', 'vehicleName',
    'ping', 'fps', 'fpsReplay', 'latency',
    'dAngleAiming', 'dAngleIdeal', 'turretRotationSpeed', 'additiveFactor', 'shotDispersionAngle', 'shotFactor',
    'aimingStartTime', 'aimingStartFactor', 'multFactor', 'factorsTurretRotation', 'factorsMovement', 'factorsRotation', 'aimingTime',
    'vehicleYaw', 'vehiclePitch', 'vehicleRoll', 'vehicleRYaw', 'turretYaw', 'gunPitch',
    'vehicleSpeed', 'vehicleRSpeed', 'engineRPM', 'engineRelativeRPM',
    'shotSpeed', 'shotSpeedH', 'shotSpeedV', 'shotGravity',
    'shotPosX', 'shotPosY', 'shotPosZ', 'shotDistance', 'shotDistanceH', 'shotDistanceV',
    'vehiclePosX', 'vehiclePosY', 'vehiclePosZ', 'distance', 'distanceH', 'distanceV',
    'targetPosX', 'targetPosY', 'targetPosZ',
    'aimingFactor', 'aimingTimeConverging', 'modifiedAimingFactor', 'scoreDispersion',
    'flightTime',
    'piercingPercent', 'targetPenetrationArmor', 'targetArmor', 'targetHitAngleCos', 'targetArmorKind', 'targetVehicleName',
    'piercingMultiplier'
]
