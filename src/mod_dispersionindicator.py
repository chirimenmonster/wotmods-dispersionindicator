
import math
import json
import BigWorld
import ResMgr
import GUI
from debug_utils import LOG_CURRENT_EXCEPTION
from gui import g_guiResetters
from gui.Scaleform.daapi.view.battle.shared.crosshair.plugins import ShotResultIndicatorPlugin

from PlayerEvents import g_playerEvents

from dispersionindicator.status import getDispersionStatsPool
from dispersionindicator.events import overrideMethod
from dispersionindicator.panel import PanelWidget, LabelWidget

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
        'bgimage':          'BGIMAGE_FILE'
    },
    'stats_defs':       {},
    'panels':           {}
}

g_panel = None

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
    global g_panel
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
        g_panel = IndicatorPanel(g_config, stats)
    except:
        LOG_CURRENT_EXCEPTION()
    g_playerEvents.onAvatarBecomePlayer += onAvatarBecomePlayer


def onAvatarBecomePlayer():
    print 'onAvatarBecomePlayer'

@overrideMethod(ShotResultIndicatorPlugin, 'start')
def shotResultIndicatorPlugin_start(orig, self, *args, **kwargs):
    result = orig(self, *args, **kwargs)
    if g_panel:
        g_panel.start()
    return result

@overrideMethod(ShotResultIndicatorPlugin, 'stop')
def shotResultIndicatorPlugin_stop(orig, self, *args, **kwargs):
    if g_panel:
        g_panel.stop()
    result = orig(self, *args, **kwargs)
    return result

@overrideMethod(ShotResultIndicatorPlugin, '_ShotResultIndicatorPlugin__onGunMarkerStateChanged')
def shotResultIndicatorPlugin_onGunMarkerStateChanged(orig, self, *args, **kwargs):
    result = orig(self, *args, **kwargs)
    if g_panel:
        g_panel.onGunMarkerStateChanged()
    return result


class IndicatorPanel(object):
    def __init__(self, config, stats):
        self.stats = stats
        default = config['default']
        self.label_font = default['font']
        self.label_colour = tuple(default['colour'] + [ default['alpha'] ])
        self.line_height = default['line_height']
        self.padding_top = default['padding_top']
        self.padding_bottom = default['padding_bottom']
        self.panel_offset = default['panel_offset']
        self.panel_width = default['panel_width']
        self.bgimage = default['bgimage']
        self.statsdefs = config['stats_defs']
        self.panel = self.createWidgetTree(config['panels']['panel0']['items'])

    def start(self):
        BigWorld.logInfo(MOD_NAME, 'panel.start', None)
        self.panel.addRoot()
        g_guiResetters.add(self.onScreenResolutionChanged)
        self.updatePosition()
        self.panel.visible = True
        
    def stop(self):
        BigWorld.logInfo(MOD_NAME, 'panel.stop', None)
        g_guiResetters.discard(self.onScreenResolutionChanged)
        self.panel.visible = False
        self.panel.delRoot()

    def toggleVisible(self):
        self.panel.visible = not self.panel.visible

    def onGunMarkerStateChanged(self):
        self.panel.update()

    def onScreenResolutionChanged(self):
        self.updatePosition()

    def updatePosition(self):
        screen = GUI.screenResolution()
        center = ( screen[0] / 2, screen[1] / 2)
        x = center[0] + self.panel_offset[0]
        y = center[1] + self.panel_offset[1]
        self.panel.position = (x, y, 1)

    def createWidgetTree(self, items):
        panel = PanelWidget(self.bgimage)
        y = self.padding_top
        for name in items:
            setting = self.statsdefs[name]
            child = self.createPanelLine(setting)
            panel.addChild(child)
            child.position = (0, y, 1)
            y = y + child.height
        panel.width = self.panel_width
        panel.height = y + self.padding_bottom
        panel.horizontalAnchor = 'RIGHT'
        panel.verticalAnchor = 'CENTER'
        return panel

    def createPanelLine(self, setting):
        name = setting['status']
        factor = setting['factor']
        template = setting['format']
        if isinstance(factor, str) or isinstance(factor, unicode):
            factor = CONSTANT.get(factor, 1.0)
        argList = [
            {
                'text':     setting['title'],
                'align':    'RIGHT',
                'x':        self.panel_width - 128
            },
            {
                'func':     lambda n=name, f=factor, t=template, s=self.stats: t.format(getattr(s, n, 0.0) * f),
                'align':    'RIGHT',
                'x':        self.panel_width - 72
            },
            {
                'text':     setting['unit'],
                'x':        self.panel_width - 60
            }
        ]
        panel = PanelWidget()
        for kwarg in argList:
            label = self.createLabel(**kwarg)
            panel.addChild(label)
        panel.width = self.panel_width
        panel.height = self.line_height
        panel.visible = True
        return panel

    def createLabel(self, text=None, func=None, align='LEFT', x=0):
        label = LabelWidget()
        if text is not None:
            label.text = text
        if func is not None:
            label.setCallback(func)
        label.font = self.label_font
        label.colour = self.label_colour
        label.horizontalAnchor = align
        label.position = (x, 0, 1)
        label.visible = True
        return label
