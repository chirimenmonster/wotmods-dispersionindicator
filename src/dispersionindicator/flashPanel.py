
import BigWorld
import GUI
from gui.Scaleform.Flash import Flash

from mod_constants import MOD_NAME, CONSTANT, CROSSHAIR_VIEW_SYMBOL

SWF_FILE = 'IndicatorPanel.swf'
SWF_PATH = '${flash_dir}'

class IndicatorFlashText(object):
    def __init__(self, config, stats, name):
        self.stats = stats
        self.name = name
        style = config['style']
        self.referencePoint = style['referencePoint']
        self.horizontalAnchor = style['horizontalAnchor']
        self.verticalAnchor = style['verticalAnchor']
        self.screenOffset = style['screenOffset']
        self.crosshairOffset = { id:style.get('crosshairOffset_' + symbol, style['crosshairOffset']) for id, symbol in CROSSHAIR_VIEW_SYMBOL.items() }
        self.statsdefs = config['statsDefs']
        flash = Flash(SWF_FILE, path=SWF_PATH)
        flash.movie.backgroundAlpha = 0.0
        flash.movie.scaleMode = 'NoScale'
        flash.component.heightMode = 'PIXEL'
        flash.component.widthMode = 'PIXEL'
        flash.component.wg_inputKeyMode = 2
        flash.component.focus = False
        flash.component.moveFocus = False
        flash.component.position.z = style['positionZ']
        self.__config = []
        for key in config['items']:
            setting = self.statsdefs[key]
            name = setting['status']
            factor = setting['factor']
            template = setting['format']
            if isinstance(factor, str) or isinstance(factor, unicode):
                factor = CONSTANT.get(factor, 1.0)
            self.__config.append({
                'name':         key,
                'label':        setting['title'],
                'unit':         setting['unit'],
                'func':         lambda n=name, f=factor, s=self.stats: getattr(s, n, 0.0) * f,
                'format':       template
            })
        print style
        flash.movie.root.as_createPanel(self.__config, style)
        self.flash = flash 
        self.__viewID = 0

    def init(self):
        BigWorld.logInfo(MOD_NAME, 'flashText.init: "{}"'.format(self.name), None)
        self.updateScreenPosition()
        for config in self.__config:
            name = config['name']
            text = config['format'].format(0)
            self.flash.movie.root.as_setValue(name, text)

    def start(self):
        BigWorld.logInfo(MOD_NAME, 'flashText.start: "{}"'.format(self.name), None)
        self.flash.active(True)

    def stop(self):
        BigWorld.logInfo(MOD_NAME, 'flashText.stop: "{}"'.format(self.name), None)
        self.flash.active(False)
   
    def update(self):
        data = getattr(self.stats, 'aimingTimeConverging', 0.0)
        for config in self.__config:
            name = config['name']
            text = config['format'].format(config['func']())
            self.flash.movie.root.as_setValue(name, text)

    def updateScreenPosition(self):
        refPoint = self.referencePoint.split('_')
        if refPoint[0] != 'SCREEN':
            return
        if len(refPoint) == 2 and refPoint[1] == 'CENTER':
            refPoint.append('CENTER')
        offsetX = offsetY = 0
        width = self.flash.movie.root.fieldWidth
        height = self.flash.movie.root.fieldHeight
        if self.horizontalAnchor == 'RIGHT':
            offsetX = - width
        elif self.horizontalAnchor == 'CENTER':
            offsetX = - width / 2
        if self.verticalAnchor == 'BOTTOM':
            offsetY = - height
        elif self.verticalAnchor == 'CENTER':
            offsetY = - height / 2
        screen = GUI.screenResolution()
        center = ( screen[0] / 2, screen[1] / 2)
        x = y = 0
        if refPoint[1] == 'CENTER':
            x = center[0] + self.screenOffset[0] + offsetX
        elif refPoint[1] == 'LEFT':
            x = self.screenOffset[0] + offsetX
        elif refPoint[1] == 'RIGHT':
            x = screen[0] + self.screenOffset[0] + offsetX
        if refPoint[2] == 'CENTER':
            y = center[1] + self.screenOffset[1] + offsetY
        elif refPoint[2] == 'TOP':
            y = self.screenOffset[1] + offsetY
        elif refPoint[2] == 'BOTTOM':
            y = screen[1] + self.screenOffset[1] + offsetY
        #BigWorld.logInfo(MOD_NAME, 'flashText.updatePosition ({}, {})'.format(x, y), None)
        self.flash.movie.root.as_setPosition(int(x), int(y))

    def updateCrosshairPosition(self, x, y):
        if self.referencePoint != 'CROSSHAIR':
            return
        #BigWorld.logInfo(MOD_NAME, 'flashText.updateCrosshairPosition ({}, {})'.format(x, y), None)
        offsetX = offsetY = 0
        width = self.flash.movie.root.fieldWidth
        height = self.flash.movie.root.fieldHeight
        if self.horizontalAnchor == 'RIGHT':
            offsetX = - width
        elif self.horizontalAnchor == 'CENTER':
            offsetX = - width / 2
        if self.verticalAnchor == 'BOTTOM':
            offsetY = - height
        elif self.verticalAnchor == 'CENTER':
            offsetY = - height / 2
        x = x + self.crosshairOffset[self.__viewID][0] + offsetX
        y = y + self.crosshairOffset[self.__viewID][1] + offsetY
        self.flash.movie.root.as_setPosition(int(x), int(y))

    def changeView(self, viewID):
        self.__viewID = viewID
        return
