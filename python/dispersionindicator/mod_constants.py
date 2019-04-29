
import math

from constants import ARENA_PERIOD
from gui.battle_control.battle_constants import CROSSHAIR_VIEW_ID
from gui.app_loader.settings import GUI_GLOBAL_SPACE_ID

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
    GUI_GLOBAL_SPACE_ID.UNDEFINED:      'UNDEFINED',
    GUI_GLOBAL_SPACE_ID.WAITING:        'WAITING',
    GUI_GLOBAL_SPACE_ID.INTRO_VIDEO:    'INTRO_VIDEO',
    GUI_GLOBAL_SPACE_ID.LOGIN:          'LOGIN',
    GUI_GLOBAL_SPACE_ID.LOBBY:          'LOBBY',
    GUI_GLOBAL_SPACE_ID.BATTLE_LOADING: 'BATTLE_LOADING',
    GUI_GLOBAL_SPACE_ID.BATTLE:         'BATTLE',
}
