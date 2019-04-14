
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

g_config = { 'default': {}, 'statsDefs': {}, 'panels': {} }

def init():
    try:
        BigWorld.logInfo(MOD_NAME, '{} initialize'.format(MOD_NAME), None)

        def encode_key(data):
            ascii_encode = lambda x: x.encode('ascii') if isinstance(x, unicode) else x
            return dict({ ascii_encode(key): value for key, value in data.items() })

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
        g_entitiesFactories.addSettings(PANEL_VIEW_SETTINGS)
        g_eventBus.addListener(events.AppLifeCycleEvent.INITIALIZED, onAppInitialized)
    except:
        LOG_CURRENT_EXCEPTION()


def onAppInitialized(event):
    if event.ns != APP_NAME_SPACE.SF_BATTLE:
        return
    BigWorld.logInfo(MOD_NAME, 'AppLifeCycleEvent.INITIALIZED', None)
    indicator = Indicator(g_config)
    for name, paneldef in g_config['panels'].items():
        localConfig = { 'style': {} }
        localConfig['style'].update(g_config['default'])
        localConfig['style'].update(paneldef.get('style', {}))
        localConfig['statsDefs'] = {}
        localConfig['statsDefs'].update(g_config['statsDefs'])
        localConfig['statsDefs'].update(paneldef.get('statsDefs', {}))
        localConfig['items'] = paneldef['items']
        indicator.addFlashPanel(name, localConfig)
    if len(g_config.get('logs', {})):
        localConfig = {}
        localConfig['items'] = g_config['logs'].values()[0]['items']
        localConfig['statsDefs'] = g_config['statsDefs']
        indicator.addLogger(localConfig)
    indicator.onAvatarBecomePlayer()
    #g_playerEvents.onAvatarBecomePlayer += indicator.onAvatarBecomePlayer
    g_playerEvents.onAvatarBecomeNonPlayer += indicator.onAvatarBecomeNonPlayer


