
import math
import json
import BigWorld
import ResMgr
from debug_utils import LOG_CURRENT_EXCEPTION
from gui.Scaleform.daapi.view.battle.shared.crosshair.plugins import ShotResultIndicatorPlugin
from PlayerEvents import g_playerEvents

from dispersionindicator.status import getDispersionStatsPool
from dispersionindicator.events import overrideMethod
from dispersionindicator.indicator import IndicatorPanel
from dispersionindicator.output import OutputFile


MOD_NAME = '${name}'

CONFIG_FILES = [
    '${resource_dir}/default.json',
    '${resource_dir}/config.json',
    '${config_file}'
]

g_config = { 'default': {}, 'stats_defs': {}, 'panels': {} }
g_panel = {}


def init():
    try:
        BigWorld.logInfo(MOD_NAME, '{} initialize'.format(MOD_NAME), None)
        for file in CONFIG_FILES:
            if not ResMgr.isFile(file):
                continue
            BigWorld.logInfo(MOD_NAME, 'load config file: {}'.format(file), None)
            section = ResMgr.openSection(file)
            data = json.loads(section.asString)
            g_config['default'].update(data.get('default', {}))
            g_config['stats_defs'].update(data.get('stats_defs', {}))
            g_config['panels'] = data.get('panels', {})
            g_config['logs'] = data.get('logs', {})
        print json.dumps(g_config, indent=2)
        stats = getDispersionStatsPool()
        for name, paneldef in g_config['panels'].items():
            config = { 'style': {} }
            config['style'].update(g_config['default'])
            config['style'].update(paneldef.get('style', {}))
            config['stats_defs'] = {}
            config['stats_defs'].update(g_config['stats_defs'])
            config['stats_defs'].update(paneldef.get('stats_defs', {}))
            config['items'] = paneldef['items']
            panel = IndicatorPanel(config, stats)
            if panel:
                g_panel[name] = panel
        if len(g_config.get('logs', {})):
            config = {}
            config['items'] = g_config['logs'].values()[0]['items']
            config['stats_defs'] = g_config['stats_defs']
            g_panel['__log__'] = OutputFile(config, stats)
    except:
        LOG_CURRENT_EXCEPTION()


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
        try:
            panel.onGunMarkerStateChanged()
        except:
            BigWorld.logError(MOD_NAME, 'fail to update panel state', None)
    return result

