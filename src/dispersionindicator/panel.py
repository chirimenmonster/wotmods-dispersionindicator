
import GUI
import ResMgr
from gui import g_guiResetters


BGIMAGE_FILE = '${resource_dir}/bgimage.dds'
DEFAULT_WIDTH = 280
DEFAULT_HEIGHT = 16

class Config:
    colour = (255, 255, 0)
    alpha = 127
    font = 'default_small.font'
    padding_top = 4
    padding_bottom = 4
    panel_width = 280
    panel_offset = (-200, 50)
    bgimage = BGIMAGE_FILE

g_config = Config()


def test():
    class LabelConfig: pass
    config = LabelConfig()
    config.title = 'Current Time'
    config.unit = 's'
    config.getStatus = lambda: BigWorld.time()
    Panel([config])


class Label(object):
    def __init__(self, horizontalAnchor='LEFT', verticalAnchor='TOP', text='', func=None, x=0, y=0):
        self.widget = GUI.Text(text)
        self.widget.horizontalPositionMode = 'PIXEL'
        self.widget.verticalPositionMode = 'PIXEL'
        self.widget.colourFormatting = True
        self.widget.font = g_config.font
        self.widget.colour = g_config.colour + (g_config.alpha, )
        self.widget.horizontalAnchor = horizontalAnchor
        self.widget.verticalAnchor = verticalAnchor
        self.widget.position = (x, y, 1)
        self.widget.visible = True
        self.__func = func

    def onUpdate(self):
        if callable(self.__func):
            self.widget.text = str(self.__func())


class PanelLine(object):
    def __init__(self, config, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT, x=0, y=0):
        self.children = []
        self.widget = GUI.Window(g_config.bgimage)
        self.widget.materialFX = 'BLEND'
        self.widget.horizontalAnchor = 'LEFT'
        self.widget.verticalAnchor = 'TOP'
        self.widget.horizontalPositionMode = 'PIXEL'
        self.widget.verticalPositionMode = 'PIXEL'
        self.widget.widthMode = 'PIXEL'
        self.widget.heightMode = 'PIXEL'
        self.widget.width = width
        self.widget.height = height
        self.widget.position = (x, y, 1)
        self.addChild(Label(text=config.title, horizontalAnchor='RIGHT', x=width-128, y=0))
        self.addChild(Label(func=config.func, horizontalAnchor='RIGHT', x=width-72, y=0))
        self.addChild(Label(text=config.unit, horizontalAnchor='LEFT', x=width-60, y=0))
        self.widget.visible = True

    def addChild(self, child):
        self.children.append(child)
        self.widget.addChild(child.widget)

    def onUpdate(self):
        for child in self.children:
            if callable(getattr(child, 'onUpdate')):
                child.onUpdate()


class Panel(object):
    def __init__(self, items=[]):
        self.children = []
        print g_config.bgimage, ResMgr.isFile(g_config.bgimage)
        self.widget = GUI.Window(g_config.bgimage)
        self.widget.materialFX = 'BLEND'
        self.widget.horizontalAnchor = 'RIGHT'
        self.widget.verticalAnchor = 'CENTER'
        self.widget.horizontalPositionMode = 'PIXEL'
        self.widget.verticalPositionMode = 'PIXEL'
        self.widget.widthMode = 'PIXEL'
        self.widget.heightMode = 'PIXEL'
        self.widget.width = g_config.panel_width
        y = g_config.padding_top
        for item in items:
            child = PanelLine(item, x=0, y=y)
            self.addChild(child)
            #y = y + child.widget.height
            y = y + DEFAULT_HEIGHT
        self.widget.height = y + g_config.padding_bottom
        self.widget.visible = False
        self.addChild(Label(text='TEST', horizontalAnchor='RIGHT', x=128, y=10))

    def addChild(self, child):
        self.children.append(child)
        self.widget.addChild(child.widget)

    def start(self):
        print 'panel.start'
        GUI.addRoot(self.widget)
        g_guiResetters.add(self.onScreenResolutionChanged)
        self.onScreenResolutionChanged()
        self.widget.visible = True

    def stop(self):
        print 'panel.stop'
        g_guiResetters.discard(self.onScreenResolutionChanged)
        GUI.delRoot(self.widget)

    def onUpdate(self):
        for child in self.children:
            if callable(getattr(child, 'onUpdate')):
                child.onUpdate()

    def onScreenResolutionChanged(self):
        screen = GUI.screenResolution()
        center = ( screen[0] / 2, screen[1] / 2)
        x = center[0] + g_config.panel_offset[0]
        y = center[1] + g_config.panel_offset[1]
        self.widget.position = (x, y, 1)
        print self.widget.position, self.widget.width, self.widget.height

    def toggleVisible(self):
        self.widget.visible = not self.widget.visible
