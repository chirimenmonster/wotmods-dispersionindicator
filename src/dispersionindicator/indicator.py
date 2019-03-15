
import BigWorld
import GUI
from gui import g_guiResetters

from widget import PanelWidget, LabelWidget

MOD_NAME = '${name}'

class IndicatorPanel(object):
    def __init__(self, config, stats):
        self.stats = stats
        style = config['style']
        self.label_font = style['font']
        self.label_colour = tuple(style['colour'] + [ style['alpha'] ])
        self.line_height = style['line_height']
        self.padding_top = style['padding_top']
        self.padding_bottom = style['padding_bottom']
        self.panel_offset = style['panel_offset']
        self.panel_width = style['panel_width']
        self.bgimage = style['bgimage']
        self.statsdefs = config['stats_defs']
        self.panel = self.createWidgetTree(config['items'])

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
        x = center[0] + self.panel_offset[0] - self.panel_envx[0]
        y = center[1] + self.panel_offset[1]
        self.panel.position = (x, y, 1)

    def createWidgetTree(self, items):
        panel = PanelWidget(self.bgimage)
        y = self.padding_top
        envx = [0, 0]
        for name in items:
            setting = self.statsdefs[name]
            child = self.createPanelLine(setting)
            panel.addChild(child)
            y = y + child.height
        anchorx = max([ c.anchor for c in panel.chidren ])
        for child in panel.children:
            pos = list(child.position)
            offsetx = anchorx - child.anchor[0]
            newpos = (pos[0] + offsetx, pos[1], pos[2])
            child.bx[0] = child.bx[0] + offsetx
            child.bx[1] = child.bx[1] + offsetx
            child.position = newpos
            print pos, newpos
        bx = [
            min([ c.bx[0] for c in panel.children]),
            max([ c.bx[1] for c in panel.children])
        ]
        panel.width = bx[1] - bx[0]
        panel.height = y + self.padding_bottom
        panel.bx = bx
        panel.horizontalAnchor = 'RIGHT'
        panel.verticalAnchor = 'CENTER'
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
                'x':        self.panel_width - 128,
                'relx':     -56
            },
            'stat': {
                'func':     lambda n=name, f=factor, t=template, s=self.stats: t.format(getattr(s, n, 0.0) * f),
                'align':    'RIGHT',
                'x':        self.panel_width - 72,
                'width':    56,
                'relx':     0
            },
            'unit': {
                'text':     setting['unit'],
                'x':        self.panel_width - 60,
                'relx':     0
            }
        }
        panel = PanelWidget(self.bgimage)
        for name, kwargs in argList.items():
            label = self.createLabel(**kwargs)
            panel.addChild(label, name)
        bx = [
            min([ c.bx[0] for c in panel.children]),
            max([ c.bx[1] for c in panel.children])
        ]
        for child in panel.children:
            pos = list(child.position)
            newpos = (pos[0] - bx[0], pos[1] - bx[0], pos[2])
            child.position = newpos
        panel.anchor = [ -bx[0], 0 ]
        panel.width = bx[1] - bx[0]
        panel.height = self.line_height
        panel.bx = [ 0, panel.width ]
        panel.visible = True
        return panel

    def createLabel(self, text='', func=None, align='LEFT', x=0, width=None, relx=0):
        label = LabelWidget()
        label.text = text
        if func is not None:
            label.setCallback(func)
        label.font = self.label_font
        label.colour = self.label_colour
        label.horizontalAnchor = align
        label.position = (relx, 0, 1)
        label.visible = True
        width = max(label.getStringWidth(), kwargs.get('width', 0))
        if align == 'RIGHT':
            label.bx = [ relx - width, relx ]
        else:
            label.bx = [ relx, relx + width ]
        return label
