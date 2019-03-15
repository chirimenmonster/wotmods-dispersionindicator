
import GUI


class Widget(object):
    @property
    def visible(self):
        return self.widget.visible

    @visible.setter
    def visible(self, visible):
        self.widget.visible = visible
    
    @property
    def width(self):
        return self.widget.width

    @width.setter
    def width(self, width):
        self.widget.width = width

    @property
    def height(self):
        return self.widget.height

    @height.setter
    def height(self, height):
        self.widget.height = height

    @property
    def horizontalAnchor(self):
        return self.widget.horizontalAnchor

    @horizontalAnchor.setter
    def horizontalAnchor(self, horizontalAnchor):
        self.widget.horizontalAnchor = horizontalAnchor

    @property
    def verticalAnchor(self):
        return self.widget.verticalAnchor

    @verticalAnchor.setter
    def verticalAnchor(self, verticalAnchor):
        self.widget.verticalAnchor = verticalAnchor

    @property
    def position(self):
        return self.widget.position

    @position.setter
    def position(self, position):
        self.widget.position = position

    @property
    def boundingBox(self):
        pos = self.position
        width = self.width
        height = self.height
        if self.horizontalAnchor == 'LEFT':
            bx = [ pos[0], pos[0] + width ]
        elif self.horizontalAnchor == 'RIGHT':
            bx = [ pos[0] - width, pos[0] ]
        elif self.horizontalAnchor == 'CENTER':
            bx = [ pos[0] - width / 2, pos[0] + width / 2 ]
        else:
            raise Exception('implement error')
        if self.verticalAnchor == 'TOP':
            by = [ pos[1], pos[1] + height ]
        elif self.verticalAnchor == 'BOTTOM':
            by = [ pos[1] - height, pos[1] ]
        elif self.verticalAnchor == 'CENTER':
            by = [ pos[1] - height / 2, pos[1] + height / 2 ]
        else:
            raise Exception('implement error')
        return ( bx[0], by[0], bx[1], by[1] )


class LabelWidget(Widget):
    def __init__(self, text=''):
        self.widget = GUI.Text(text)
        self.widget.horizontalPositionMode = 'PIXEL'
        self.widget.verticalPositionMode = 'PIXEL'
        self.widget.colourFormatting = True
        self.horizontalAnchor = 'LEFT'
        self.verticalAnchor = 'TOP'
        self.__func = None
        self.__explicitWidth = None

    def update(self):
        if callable(self.__func):
            self.text = str(self.__func())

    def setCallback(self, callback):
        self.__func = callback

    def getStringWidth(self):
        return self.widget.stringWidth(self.text)
    
    @property
    def text(self):
        return self.widget.text

    @text.setter
    def text(self, text):
        self.widget.text = text

    @property
    def width(self):
        if self.__explicitWidth is not None:
            return self.__explicitWidth
        return self.getStringWidth()

    @width.setter
    def width(self, width):
        self.__explicitWidth = width

    @property
    def font(self):
        return self.widget.font

    @font.setter
    def font(self, font):
        self.widget.font = font

    @property
    def colour(self):
        return self.widget.colour

    @colour.setter
    def colour(self, colour):
        self.widget.colour = colour

    @property
    def explicitSize(self):
        return self.widget.explicitSize

    @explicitSize.setter
    def explicitSize(self, explicitSize):
        self.widget.explicitSize = explicitSize


class PanelWidget(Widget):
    def __init__(self, bgimage=''):
        self.children = []
        self.__children = {}
        self.widget = GUI.Window(bgimage)
        self.widget.materialFX = 'BLEND'
        self.widget.horizontalPositionMode = 'PIXEL'
        self.widget.verticalPositionMode = 'PIXEL'
        self.widget.widthMode = 'PIXEL'
        self.widget.heightMode = 'PIXEL'
        self.horizontalAnchor = 'LEFT'
        self.verticalAnchor = 'TOP'

    def addChild(self, child, name=None):
        self.children.append(child)
        if name is not None:
            self.__children[name] = child
        self.widget.addChild(child.widget)

    def getChild(self, name):
        return self.__children.get(name, None)

    def update(self):
        for child in self.children:
            if callable(getattr(child, 'update')):
                child.update()

    def addRoot(self):
        GUI.addRoot(self.widget)

    def delRoot(self):
        GUI.delRoot(self.widget)

