
import logging
import math
import json
import ResMgr
from debug_utils import LOG_CURRENT_EXCEPTION
from gui.Scaleform.framework import g_entitiesFactories

from dispersionindicator.mod_constants import MOD, CONFIG_FILES, EVENT, EVENT_LIST
from dispersionindicator.manager import IndicatorManager
from dispersionindicator.view.panelview import PANEL_VIEW_SETTINGS

_logger = logging.getLogger(MOD.NAME)

g_indicatorManager = None

def getLogLevel(name):
    logLevel = {
        'CRITICAL':     logging.CRITICAL,
        'ERROR':        logging.ERROR,
        'WARNING':      logging.WARNING,
        'INFO':         logging.INFO,
        'DEBUG':        logging.DEBUG,
        'NOTSET':       logging.NOTSET
    }
    return logLevel.get(name, logging.INFO)

def init():
    global g_indicatorManager
    try:
        _logger.info('initialize: %s %s', MOD.PACKAGE_ID, MOD.VERSION)
        settings = _readConfig()
        logLevel = getLogLevel(settings['common'].get('logLevel', 'INFO'))
        _logger.setLevel(logLevel)
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
        _logger.info('load config file: %s', file)
        section = ResMgr.openSection(file)
        data = json.loads(section.asString, object_hook=encode_key)
        config['default'].update(data.get('default', {}))
        config['statsDefs'].update(data.get('statsDefs', {}))
        config['panels'] = data.get('panels', {})
        config['loggers'] = data.get('loggers', {})
    #print json.dumps(config, indent=2)

    settings = { 'common': {}, 'panels': {}, 'loggers': {}, 'eventloggers': {} }
    settings['common']['logLevel'] = config['default']['logLevel']
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
    for name, paneldef in config.get('loggers', {}).items():
        statsDef = {}
        statsDef.update(config['statsDefs'])
        statsDef.update(paneldef.get('statsDefs', {}))
        items = paneldef['items']
        channel = paneldef['channel']
        logfile = paneldef['logfile']
        panelconf = { 'channel': channel, 'logfile': logfile, 'statsDefs': statsDef, 'items': items }
        if channel == 'status':
            settings['loggers'][name] = panelconf
        elif channel == 'event':
            print json.dumps(EVENT_LIST, indent=2)
            print json.dumps(paneldef.get('events', []), indent=2)
            panelconf['events'] = [ e for e in EVENT_LIST if e in paneldef.get('events', []) ]
            settings['eventloggers'][name] = panelconf
    print json.dumps(settings['loggers'], indent=2)
    print json.dumps(settings['eventloggers'], indent=2)

    return settings

