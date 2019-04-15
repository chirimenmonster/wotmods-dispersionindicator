
import math
import json
import BigWorld
import ResMgr
from debug_utils import LOG_CURRENT_EXCEPTION
from PlayerEvents import g_playerEvents
from Avatar import PlayerAvatar
from gui.shared import g_eventBus, events
from gui.app_loader.settings import APP_NAME_SPACE
from gui.Scaleform.framework import g_entitiesFactories

from dispersionindicator.mod_constants import MOD_NAME, CONFIG_FILES
from dispersionindicator.indicator import Indicator
from dispersionindicator.view.panelview import PANEL_VIEW_SETTINGS

g_config = {}
g_indicator = None

def init():
    try:
        BigWorld.logInfo(MOD_NAME, '{} initialize'.format(MOD_NAME), None)
        _readConfig()
        g_entitiesFactories.addSettings(PANEL_VIEW_SETTINGS)
        g_eventBus.addListener(events.AppLifeCycleEvent.INITIALIZED, onAppInitialized)
        g_eventBus.addListener(events.AppLifeCycleEvent.DESTROYED, onAppDestroyed)
    except:
        LOG_CURRENT_EXCEPTION()


def _readConfig():
    def encode_key(data):
        ascii_encode = lambda x: x.encode('ascii') if isinstance(x, unicode) else x
        return dict({ ascii_encode(key): value for key, value in data.items() })

    g_config['default'] = {}
    g_config['statsDefs'] = {}
    g_config['panels'] = {}
    
    for file in CONFIG_FILES:
        if not ResMgr.isFile(file):
            continue
        BigWorld.logInfo(MOD_NAME, 'load config file: {}'.format(file), None)
        section = ResMgr.openSection(file)
        data = json.loads(section.asString, object_hook=encode_key)
        g_config['default'].update(data.get('default', {}))
        g_config['statsDefs'].update(data.get('statsDefs', {}))
        g_config['panels'] = data.get('panels', {})
        g_config['logs'] = data.get('logs', {})
    print json.dumps(g_config, indent=2)


def onAppInitialized(event):
    if event.ns != APP_NAME_SPACE.SF_BATTLE:
        return
    BigWorld.logInfo(MOD_NAME, 'AppLifeCycleEvent.INITIALIZED: SF_BATTLE', None)
    global g_indicator
    g_indicator = Indicator(g_config)
    g_indicator.initPanel()
    #g_playerEvents.onAvatarBecomeNonPlayer += indicator.onAvatarBecomeNonPlayer

def onAppDestroyed(event):
    if event.ns != APP_NAME_SPACE.SF_BATTLE:
        return
    BigWorld.logInfo(MOD_NAME, 'AppLifeCycleEvent.DESTROYED: SF_BATTLE', None)
    global g_indicator
    if g_indicator:
        g_indicator.finiPanel()
        g_indicator = None
