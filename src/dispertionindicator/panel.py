
import GUI


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


class Label(GUI.TextGUIComponent):
    def __init__(self, horizontalAnchor='LEFT', verticalAnchor='TOP', text='', func=None, x=0, y=0):
        super(Label, self).__init__(text)
        self.horizontalPositionMode = 'PIXEL'
        self.verticalPositionMode = 'PIXEL'
        self.colourFormatting = True
        self.font = g_config.font
        self.colour = (*g_config.colour, g_config.alpha)
        self.horizontalAncor = horizontalAnchor
        self.verticalAnchor = verticalAnchor
        self.position = (x, y, 1)
        self.visible = True
        self.__func = func

    def onUpdate(self):
        if callable(self.__func):
            self.text = str(self.__func())


class PanelLine(GUI.SimpleGUIComponent):
    def __init__(self, config, width=DEFALT_WIDTH, height=DEFAULT_HEIGHT):
        super(PanelLine, self).__init__()
        self.materialFX = 'BLEND'
        self.horizontalPositionMode = 'PIXEL'
        self.verticalPositionMode = 'PIXEL'
        self.widthMode = 'PIXEL'
        self.heightMode = 'PIXEL'
        self.addChild(Label(text=config.title, horizontanAnchor='RIGHT', x=width-128, y=0), 'labelTitle')
        self.addChild(Label(func=config.func, horizontalAnchor='RIGHT', x=width-72, y=0), 'labelStatus')
        self.addChild(Label(text=config.unit, horizontalAnchor='LEFT', x=width-60, y=0), 'labelUnit')
        self.visible = True

    def onUpdate(self):
        self.labelStatus.onUpdate()


class Panel(GUI.SimpleGUIComponent):
    def __init__(self, items=[]):
        super(Panel, self).__init__(g_config.bg_image)
        self.horizontalAnchor = 'RIGHT'
        self.verticalAnchor = 'CENTER'
        self.horizontalPositionMode = 'PIXEL'
        self.verticalPositionMode = 'PIXEL'
        self.widthMode = 'PIXEL'
        self.heightMode = 'PIXEL'
        self.width = g_config.panel_width
        y = g_config.padding_top
        for item in items:
            widget = PanelLine(item.config, x=0, y=y)
            self.addChild(widget)
            y = y + widget.height
        self.height = y + g_config.padding_bottom
        self.visible = False

    def start(self):
        GUI.addRoot(self)
        g_guiResetters.add(self.onScreenResolutionChanged)
        self.onScreenResolutionChanged()
        self.visible = True

    def stop(self):
        g_guiResetters.discard(self.onScreenResolutionChanged)
        GUI.delRoot(self)

    def onUpdate(self):
        for widget in self.children:
            if callable(getattr(widget, onUpdate)):
                widget.onUpdate()

    def onScreenResolutionChanged(self):
        screen = GUI.screenResolution()
        center = ( screen[0] / 2, screen[1] / 2)
        x = center[0] + g_config.panel_offset[0]
        y = center[1] + g_config.panel_offset[1]
        self.position = (x, y, 1)

    def toggleVisible(self):
        self.visible = not self.visible
