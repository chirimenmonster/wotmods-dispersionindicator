
import math
import json
import BigWorld
import ResMgr
from debug_utils import LOG_CURRENT_EXCEPTION

from PlayerEvents import g_playerEvents

from dispersionindicator.status import getDispersionStatsPool
from dispersionindicator.events import overrideMethod
from dispersionindicator.indicator import IndicatorPanel

MOD_NAME = '${name}'
LOG_FILE = '${logfile}'
BGIMAGE_FILE = '${resource_dir}/bgimage.dds'
DEFAULT_CONFIG_FILE = '${resource_dir}/config.json'
CONFIG_FILE = '${config_file}'

CONSTANT = {
    'MS_TO_KMH':    3600.0 / 1000.0
}

g_config = {
    'default': {
        'colour':           [ 255, 255, 0 ],
        'alpha':            127,
        'font':             'default_small.font',
        'padding_top':      4,
        'padding_bottom':   4,
        'panel_width':      280,
        'panel_offset':     [ -200, 50 ],
        'line_height':      16,
        'bgimage':          BGIMAGE_FILE
    },
    'stats_defs':       {},
    'panels':           {}
}

g_panel = {}

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


def init():
    try:
        BigWorld.logInfo(MOD_NAME, '{} initialize'.format(MOD_NAME), None)
        if not ResMgr.isFile(DEFAULT_CONFIG_FILE):
            BigWorld.logError(MOD_NAME, 'default config is not found: {}'.format(DEFAULT_CONFIG_FILE), None)
            raise Exception
        else:
            file = ResMgr.openSection(DEFAULT_CONFIG_FILE)
            data = json.loads(file.asString)
            g_config['default'].update(data['default'])
            g_config['stats_defs'].update(data['stats_defs'])
            g_config['panels'].update(data['panels'])
        if ResMgr.isFile(CONFIG_FILE):
            BigWorld.logInfo(MOD_NAME, 'load config file: {}'.format(CONFIG_FILE), None)
            file = ResMgr.openSection(CONFIG_FILE)
            data = json.loads(file.asString)
            g_config['default'].update(data.get('default', {}))
            g_config['stats_defs'].update(data.get('stats_defs', {}))
            g_config['panels'].update(data.get('panels', {}))
            print json.dumps(g_config, indent=2)
        stats = getDispersionStatsPool()
        for name, paneldef in g_config['panels'].items():
            config = { 'style': {} }
            config['style'].udate(g_config['default'])
            config['style'].udate(paneldef['style'])
            config['stats_defs'] = g_config['stats_defs']
            config['items'] = paneldef['items']
            panel = IndicatorPanel(config, stats)
            if panel:
                g_panel[name] = panel
    except:
        LOG_CURRENT_EXCEPTION()
    g_playerEvents.onAvatarBecomePlayer += onAvatarBecomePlayer


def onAvatarBecomePlayer():
    print 'onAvatarBecomePlayer'

@overrideMethod(ShotResultIndicatorPlugin, 'start')
def shotResultIndicatorPlugin_start(orig, self, *args, **kwargs):
    result = orig(self, *args, **kwargs)
    for panel in g_panel.values():
        panel.start()
    return result

@overrideMethod(ShotResultIndicatorPlugin, 'stop')
def shotResultIndicatorPlugin_stop(orig, self, *args, **kwargs):
    for panel in g_panel.values():
        panel.stop()
    result = orig(self, *args, **kwargs)
    return result

@overrideMethod(ShotResultIndicatorPlugin, '_ShotResultIndicatorPlugin__onGunMarkerStateChanged')
def shotResultIndicatorPlugin_onGunMarkerStateChanged(orig, self, *args, **kwargs):
    result = orig(self, *args, **kwargs)
    for panel in g_panel.values():
        panel.onGunMarkerStateChanged()
    return result

