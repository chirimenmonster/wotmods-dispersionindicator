
from gui.battle_control.battle_constants import CROSSHAIR_VIEW_ID

MOD_NAME = '${name}'

CONFIG_FILES = [
    '${resource_dir}/default.json',
    '${resource_dir}/config.json',
    '${config_file}'
]

LOG_FILE = '${log_file}'

CONSTANT = {
    'MS_TO_KMH':    3600.0 / 1000.0
}

CROSSHAIR_VIEW_SYMBOL = {
    CROSSHAIR_VIEW_ID.UNDEFINED:    'UNDEFINED',
    CROSSHAIR_VIEW_ID.ARCADE:       'ARCADE',
    CROSSHAIR_VIEW_ID.SNIPER:       'SNIPER',
    CROSSHAIR_VIEW_ID.STRATEGIC:    'STRATEGIC',
    CROSSHAIR_VIEW_ID.POSTMORTEM:   'POSTMORTEM'
}

