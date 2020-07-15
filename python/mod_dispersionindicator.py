
import logging
import math
import json
from collections import OrderedDict

import ResMgr
from debug_utils import LOG_CURRENT_EXCEPTION
from gui.Scaleform.framework import g_entitiesFactories

from dispersionindicator.mod_constants import MOD, CONFIG_FILES, EVENT, EVENT_LIST, CLIENT_STATUS_LIST
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


def _validationItems(items):
    validItems = filter(lambda x: x in CLIENT_STATUS_LIST, items)
    invalidItems = filter(lambda x: x not in CLIENT_STATUS_LIST, items)
    if invalidItems:
        _logger.error('invalid items: %s' % ', '.join(invalidItems))
    return validItems

def _readConfig():
    def encode_key(data):
        ascii_encode = lambda x: x.encode('ascii') if isinstance(x, unicode) else x
        return OrderedDict([ (ascii_encode(key), value) for key, value in data ])

    config = OrderedDict([ ('default', OrderedDict()), ('statsDefs', OrderedDict()) ])
    
    for file in CONFIG_FILES:
        if not ResMgr.isFile(file):
            continue
        _logger.info('load config file: %s', file)
        section = ResMgr.openSection(file)
        data = json.loads(section.asString, object_pairs_hook=encode_key)
        config['default'].update(data.get('default', {}))
        config['statsDefs'].update(data.get('statsDefs', {}))
        config['panelDefs'] = OrderedDict()
        panels = data.get('panels', OrderedDict())
        for name, panelDef in panels.items():
            panelDef['name'] = name
            panelDef['channel'] = 'indicator'
            config['panelDefs'][name] = panelDef
        loggers = data.get('loggers', {})
        for name, panelDef in loggers.items():
            panelDef['name'] = name
            config['panelDefs'][name] = panelDef

    #_logger.info('read config:')
    #_logger.info(json.dumps(data, indent=2))

    settings = { 'common': {}, 'panelDefs': [] }
    settings['common']['logLevel'] = config['default']['logLevel']
    settings['common']['updateInterval'] = config['default']['updateInterval']

    for name, panelDef in config['panelDefs'].items():
        settings['panelDefs'].append(panelDef)
        panelDef['items'] = _validationItems(panelDef['items'])
        statsDefs = {}
        statsDefs.update(config['statsDefs'])
        statsDefs.update(panelDef.get('statsDefs', {}))
        panelDef['statsDefs'] = statsDefs
        if panelDef['channel'] == 'indicator':
            style = {}
            style.update(config['default'])
            style.update(panelDef.get('style', {}))
            panelDef['style'] = style
        elif panelDef['channel'] == 'event' or panelDef['channel'] == 'indicator':
            panelDef['events'] = [ e for e in EVENT_LIST if e in panelDef.get('events', []) ]
    #print json.dumps(settings, indent=2)

    return settings
