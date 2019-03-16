
import BigWorld
import GUI
from gui import g_guiResetters

from widget import PanelWidget, LabelWidget

MOD_NAME = '${name}'

CONSTANT = {
    'MS_TO_KMH':    3600.0 / 1000.0
}

class IndicatorPanel(object):
    def __init__(self, config, stats):
        self.stats = stats
        style = config['style']
        self.label_font = style['font']
        self.label_colour = tuple(style['colour'] + [ style['alpha'] ])
        self.line_height = style['line_height']
        self.padding_top = style['padding_top']
        self.padding_bottom = style['padding_bottom']
        self.padding_left = style['padding_left']
        self.padding_right = style['padding_right']
        self.panel_offset = style['panel_offset']
        self.panel_horizontalAnchor = str(style['horizontalAnchor'])
        self.panel_verticalAnchor = str(style['verticalAnchor'])
        self.stats_width = style['stats_width']
        self.bgimage = style['bgimage']
        self.statsdefs = config['stats_defs']
        self.panel = self.createWidgetTree(config['items'])
        self.panel.visible = False

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

    def enable(self):
        self.panel.visible = True
    
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
        anchorx = max([ c.anchor[0] for c in panel.children ])
        for child in panel.children:
            pos = list(child.position)
            offsetx = anchorx - child.anchor[0]
            newpos = (pos[0] + offsetx + self.padding_left, pos[1], pos[2])
            child.position = newpos
        bx0 = min([ c.boundingBox[0] for c in panel.children])
        bx1 = max([ c.boundingBox[2] for c in panel.children])
        panel.width = bx1 - bx0 + self.padding_left + self.padding_right
        panel.height = y + self.padding_bottom
        panel.horizontalAnchor = self.panel_horizontalAnchor
        panel.verticalAnchor = self.panel_verticalAnchor
        return panel

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
                'x':        - self.stats_width - 4
            },
            'stat': {
                'text':     template.format(0.0),
                'func':     lambda n=name, f=factor, t=template, s=self.stats: t.format(getattr(s, n, 0.0) * f),
                'align':    'RIGHT',
                'width':    self.stats_width,
                'x':        0
            },
            'unit': {
                'text':     setting['unit'],
                'x':        4
            }
        }
        panel = PanelWidget('')
        for name, kwargs in argList.items():
            label = self.createLabel(**kwargs)
            panel.addChild(label, name)
        bx0 = min([ c.boundingBox[0] for c in panel.children])
        bx1 = max([ c.boundingBox[2] for c in panel.children])
        for child in panel.children:
            pos = list(child.position)
            newpos = (pos[0] - bx0, pos[1], pos[2])
            child.position = newpos
        panel.anchor = [ - bx0, 0 ]
        panel.width = bx1 - bx0
        panel.height = self.line_height
        panel.visible = True
        panel.position = (0, 0, 1)
        return panel

    def createLabel(self, text='', func=None, align='LEFT', width=None, x=0):
        label = LabelWidget()
        label.text = text
        if func is not None:
            label.setCallback(func)
        label.font = self.label_font
        label.colour = self.label_colour
        label.horizontalAnchor = align
        label.position = (x, 0, 1)
        label.visible = True
        label.width = width
        return label
