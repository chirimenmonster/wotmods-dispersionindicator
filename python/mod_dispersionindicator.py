
import logging
import math
import json
from collections import OrderedDict

import ResMgr
from debug_utils import LOG_CURRENT_EXCEPTION


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
    try:
        from gui.Scaleform.framework import g_entitiesFactories
        from dispersionindicator.mod_constants import MOD
        from dispersionindicator.manager import IndicatorManager
        from dispersionindicator.view.panelview import PANEL_VIEW_SETTINGS
        from dispersionindicator.test import dummy

        global _logger
        _logger = logging.getLogger(MOD.NAME)
        _logger.info('initialize: %s %s', MOD.PACKAGE_ID, MOD.VERSION)
        settings = _readConfig()
        logLevel = getLogLevel(settings['common'].get('logLevel', 'INFO'))
        _logger.setLevel(logLevel)
        global g_indicatorManager
        g_indicatorManager = IndicatorManager(settings)
        g_entitiesFactories.addSettings(PANEL_VIEW_SETTINGS)
    except:
        LOG_CURRENT_EXCEPTION()


def _validationItems(items, statDefs):
    from dispersionindicator.mod_constants import CLIENT_STATUS_LIST

    validItems = []
    invalidItems = []
    for name in items:
        desc = statDefs.get(name, None) 
        statusName = desc['status'] if desc is not None else name
        if statusName in CLIENT_STATUS_LIST:
            validItems.append(name)
        else:
            invalidItems.append(name)
    if invalidItems:
        _logger.error('invalid items: %s' % ', '.join(invalidItems))
    return validItems

def _readConfig():
    from dispersionindicator.mod_constants import CONFIG_FILES, EVENT_LIST
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
        statsDefs = {}
        statsDefs.update(config['statsDefs'])
        statsDefs.update(panelDef.get('statsDefs', {}))
        panelDef['statsDefs'] = statsDefs
        panelDef['items'] = _validationItems(panelDef['items'], statsDefs)
        if panelDef['channel'] == 'indicator':
            style = {}
            style.update(config['default'])
            style.update(panelDef.get('style', {}))
            panelDef['style'] = style
        elif panelDef['channel'] == 'event' or panelDef['channel'] == 'indicator':
            panelDef['events'] = [ e for e in EVENT_LIST if e in panelDef.get('events', []) ]
    #print json.dumps(settings, indent=2)

    return settings
