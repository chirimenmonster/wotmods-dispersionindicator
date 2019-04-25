
import math
import json
import BigWorld
import ResMgr
from debug_utils import LOG_CURRENT_EXCEPTION
from gui.Scaleform.framework import g_entitiesFactories

from dispersionindicator.mod_constants import MOD_NAME, CONFIG_FILES
from dispersionindicator.manager import IndicatorManager
from dispersionindicator.view.panelview import PANEL_VIEW_SETTINGS

g_indicatorManager = None

def init():
    global g_indicatorManager
    try:
        BigWorld.logInfo(MOD_NAME, '{} initialize'.format(MOD_NAME), None)
        settings = _readConfig()
        g_indicatorManager = manager = IndicatorManager(settings)
        g_entitiesFactories.addSettings(PANEL_VIEW_SETTINGS)
    except:
        LOG_CURRENT_EXCEPTION()


def _readConfig():
    def encode_key(data):
        ascii_encode = lambda x: x.encode('ascii') if isinstance(x, unicode) else x
        return dict({ ascii_encode(key): value for key, value in data.items() })

    config = { 'default': {}, 'statsDefs': {} }
    
    for file in CONFIG_FILES:
        if not ResMgr.isFile(file):
            continue
        BigWorld.logInfo(MOD_NAME, 'load config file: {}'.format(file), None)
        section = ResMgr.openSection(file)
        data = json.loads(section.asString, object_hook=encode_key)
        config['default'].update(data.get('default', {}))
        config['statsDefs'].update(data.get('statsDefs', {}))
        config['panels'] = data.get('panels', {})
        config['logs'] = data.get('logs', {})
    #print json.dumps(config, indent=2)

    settings = { 'common': {}, 'panels': {} }
    settings['common']['updateInterval'] = config['default']['updateInterval']
    for name, paneldef in config['panels'].items():
        style = {}
        style.update(config['default'])
        style.update(paneldef.get('style', {}))
        statsDef = {}
        statsDef.update(config['statsDefs'])
        statsDef.update(paneldef.get('statsDefs', {}))
        items = paneldef['items']
        settings['panels'][name] = { 'style': style, 'statsDefs': statsDef, 'items': items }
    if len(config.get('logs', {})):
        statsDefs = config['statsDefs']
        items = config['logs'].values()[0]['items']
        settings['logs'] = { 'statsDefs': statsDef, 'items': items }
    return settings

