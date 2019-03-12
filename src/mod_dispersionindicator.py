
import math
import json
import BigWorld
import ResMgr
import GUI
from debug_utils import LOG_CURRENT_EXCEPTION
from gui import g_guiResetters
from gui.Scaleform.daapi.view.battle.shared.crosshair.plugins import ShotResultIndicatorPlugin
from Avatar import PlayerAvatar
from items.components import component_constants

from dispersionindicator.events import overrideMethod
from dispersionindicator import panel
from dispersionindicator import status

MOD_NAME = '${name}'
LOG_FILE = '${logfile}'
BGIMAGE_FILE = '${resource_dir}/bgimage.dds'
DEFAULT_CONFIG_FILE = '${resource_dir}/config.json'
CONFIG_FILE = '${config_file}'


def outputLog():
    import os
    import csv
    
    try:
        os.makedirs(os.path.dirname(LOG_FILE))
    except:
        # LOG_CURRENT_EXCEPTION()
        pass
    with open(LOG_FILE, 'wb') as f:
        writer = csv.writer(f, dialect='excel')
        writer.writerows(_strage.data)


@overrideMethod(PlayerAvatar, 'getOwnVehicleShotDispersionAngle')
def playerAvatarAddon_getOwnVehicleShotDispersionAngle(orig, self, turretRotationSpeed, withShot = 0):
    result = orig(self, turretRotationSpeed, withShot)
    status.playerAvatar_getOwnVehicleShotDispersionAngle(orig, self, turretRotationSpeed, withShot = withShot)
    return result

@overrideMethod(ShotResultIndicatorPlugin, 'start')
def shotResultIndicatorPlugin_start(orig, self, *args, **kwargs):
    result = orig(self, *args, **kwargs)
    status.g_panel.start()
    return result

@overrideMethod(ShotResultIndicatorPlugin, 'stop')
def shotResultIndicatorPlugin_stop(orig, self, *args, **kwargs):
    sttaus.g_panel.stop()
    result = orig(self, *args, **kwargs)
    return result

@overrideMethod(ShotResultIndicatorPlugin, '_ShotResultIndicatorPlugin__onGunMarkerStateChanged')
def shotResultIndicatorPlugin_onGunMarkerStateChanged(orig, self, *args, **kwargs):
    result = orig(self, *args, **kwargs)
    status.g_panel.onGunMarkerStateChanged()
    return result


def init():
    try:
        BigWorld.logInfo(MOD_NAME, '{} initialize'.format(MOD_NAME), None)
        if not ResMgr.isFile(DEFAULT_CONFIG_FILE):
            BigWorld.logInfo(MOD_NAME, 'file is not found: {}'.format(DEFAULT_CONFIG_FILE), None)
            raise
        file = ResMgr.openSection(DEFAULT_CONFIG_FILE)
        config = json.loads(file.asString)
        print json.dumps(config, indent=2)
        if ResMgr.isFile(CONFIG_FILE):
            BigWorld.logInfo(MOD_NAME, 'found config: {}'.format(CONFIG_FILE), None)
            file = ResMgr.openSection(CONFIG_FILE)
            config = json.loads(file.asString)
            print json.dumps(config, indent=2)
            BigWorld.logInfo(MOD_NAME, 'load config: {}'.format(CONFIG_FILE), None)
        status.g_config.config = config
        status.init()
    except:
        LOG_CURRENT_EXCEPTION()

