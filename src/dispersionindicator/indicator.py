
import BigWorld
from gui import g_guiResetters

from widget import PanelWidget, LabelWidget


class IndicatorPanel(object):
    def __init__(self, config, stats):
        self.stats = stats
        style = config['styles']
        self.label_font = style['font']
        self.label_colour = tuple(style['colour'] + [ style['alpha'] ])
        self.line_height = style['line_height']
        self.padding_top = style['padding_top']
        self.padding_bottom = style['padding_bottom']
        self.panel_offset = style['panel_offset']
        self.panel_width = style['panel_width']
        self.bgimage = style['bgimage']
        self.statsdefs = config['stats_defs']
        self.panel, self.panel_envx = self.createWidgetTree(config['items'])

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
        x = center[0] + self.panel_offset[0] - self.panel_envx[1]
        y = center[1] + self.panel_offset[1]
        self.panel.position = (x, y, 1)

    def createWidgetTree(self, items):
        panelPanelWidget(self.bgimage)
        y = self.padding_top
        envx = [0, 0]
        for name in items:
            setting = self.statsdefs[name]
            child, posx = self.createPanelLine(setting)
            panel.addChild(child)
            child.position = (0, y, 1)
            y = y + child.height
            envx = [min(envx[0] , posx[0]), max(envx[1] , posx[1])]
        panel.width = envx[1] - envx[0]
        panel.height = y + self.padding_bottom
        panel.horizontalAnchor = 'RIGHT'
        panel.verticalAnchor = 'CENTER'
        return panel, envx

    def createPanelLine(self, setting):
        name = setting['status']
        factor = setting['factor']
        template = setting['format']
        if isinstance(factor, str) or isinstance(factor, unicode):
            factor = CONSTANT.get(factor, 1.0)
        argList = {
            'title': {
                'text':     setting['title'],
                'align':    'RIGHT',
                'x':        self.panel_width - 128,
                'relx':     -56
            },
            'stat': {
                'func':     lambda n=name, f=factor, t=template, s=self.stats: t.format(getattr(s, n, 0.0) * f),
                'align':    'RIGHT',
                'x':        self.panel_width - 72,
                'width':    56  # 128 - 72,
                'relx':     0
            },
            'unit': {
                'text':     setting['unit'],
                'x':        self.panel_width - 60,
                'relx':     0
            }
        }
        panel = PanelWidget()
        envx = [0, 0]
        for name, kwarg in argList.items():
            label = self.createLabel(**kwarg)
            panel.addChild(label, name)
            w = max(label.getStringWidth(), kwargs.get('width', 0))
            if kwargs.get('align', None) == 'RIGHT':
                posx = [-w, 0]
            else:
                posx = [0, w]                
            posx = [ x + kwargs['relx'] for x in posx ]
            envx = [min(envx[0] , posx[0]), max(envx[1] , posx[1])]
        panel.width = envx[1] - envx[0]
        panel.height = self.line_height
        panel.visible = True
        return panel, envx

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
