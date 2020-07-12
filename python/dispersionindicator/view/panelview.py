
import logging
import BigWorld
from gui.Scaleform.framework import ViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.framework.entities.View import View
from gui.battle_control.battle_constants import CROSSHAIR_VIEW_ID

from ..mod_constants import MOD, CONSTANT, CROSSHAIR_VIEW_SYMBOL

_logger = logging.getLogger(MOD.NAME)
#_logger.setLevel(logging.DEBUG)

PANEL_VIEW_ALIAS = 'DispersionIndicatorPanel'
PANEL_VIEW_SWF_FILE_PATH = 'dispersionindicator/IndicatorPanel.swf'

class PanelView(View):
    def __init__(self, config=None, *args, **kwargs):
        super(PanelView, self).__init__(*args, **kwargs)
        self.className = self.__class__.__name__
        self.__wasPopulated = False
        self.__settings = config
        style = config['style']
        r = style['referencePoint'].split('_')
        if r[0] == 'SCREEN':
            if len(r) == 2 and r[1] == 'CENTER':
                r.append('CENTER')
            self.__reference = r[0]
            self.__referencePoint = [ r[1], r[2] ]
        elif r[0] == 'CROSSHAIR':
            self.__reference = r[0]
        else:
            raise 'unknown referncePoint: {}'.format(style['referencePoint'])
        self.__align = [ style['horizontalAnchor'], style['verticalAnchor'] ]
        self.__offset = style['screenOffset']
        self.__crosshairOffset = {}
        self.__crosshairPosition = None
        for id, symbol in CROSSHAIR_VIEW_SYMBOL.items():
            self.__crosshairOffset[id] = style.get('crosshairOffset_' + symbol, style['crosshairOffset'])
        self.__crosshairView = CROSSHAIR_VIEW_ID.UNDEFINED
        self.onCreate += self.beforeCreate
        self.onCreated += self.afterCreate

    def beforeCreate(self, pyEntity):
        _logger.debug('%s.beforeCreate', self.className)
        self.flashObject.as_setConfig(self.__settings)

    def afterCreate(self, pyEntity):
        _logger.debug('%s.afterCreate', self.className)
        self.__wasPopulated = True
        self.setPosition()
    
    def as_setPositionS(self, x, y):
        _logger.debug('%s.as_setPositionS: (%d, %d)', self.className, x, y)
        self.flashObject.as_setPosition(x, y)

    def as_setValueS(self, name, value):
        if not self.__wasPopulated:
            return
        #_logger.debug('%s.as_setValueS: name=%s, value=%s', self.className, name, value)
        self.flashObject.as_setValue(name, value)

    def as_getPanelSizeS(self):
        _logger.debug('%s.as_getPanelSizeS', self.className)
        result = self.flashObject.as_getPanelSize()
        return result.width, result.height

    def setScreenResolution(self, width, height):
        self.__screenSize = [ width, height ]

    def setCrosshairPosition(self, x, y):
        _logger.debug('%s.setCrosshairPosition: [%s, %s]', self.className, x, y)
        self.__crosshairPosition = [ x, y ]

    def setCrosshairView(self, crosshairView):
        self.__crosshairView = crosshairView

    def setVisible(self, isVisible):
        _logger.debug('%s.setVisible: %s', self.className, isVisible)
        if self.flashObject:
            self.flashObject.visible = isVisible

    def setPosition(self):
        _logger.debug('%s.setPosition: %s', self.className, self.__reference)
        if self.__reference == 'SCREEN':
            self.setPositionByScreen()
        elif self.__reference == 'CROSSHAIR':
            self.setPositionByCrosshair()

    def setPositionByScreen(self):
        if not self.__wasPopulated:
            return
        if self.__reference != 'SCREEN':
            return
        _logger.debug('%s.setPositionByScreen: %s', self.className, self.__align)
        width, height = self.as_getPanelSizeS()
        offsetX = offsetY = 0
        halign, valign = self.__align
        if halign == 'RIGHT':
            offsetX = - width
        elif halign == 'CENTER':
            offsetX = - width / 2
        if valign == 'BOTTOM':
            offsetY = - height
        elif valign == 'CENTER':
            offsetY = - height / 2
        center = ( self.__screenSize[0] / 2, self.__screenSize[1] / 2)
        x = y = 0
        if self.__referencePoint[0] == 'CENTER':
            x = center[0] + self.__offset[0] + offsetX
        elif self.__referencePoint[0] == 'LEFT':
            x = self.__offset[0] + offsetX
        elif self.__referencePoint[0] == 'RIGHT':
            x = self.__screenSize[0] + self.__offset[0] + offsetX
        if self.__referencePoint[1] == 'CENTER':
            y = center[1] + self.__offset[1] + offsetY
        elif self.__referencePoint[1] == 'TOP':
            y = self.__offset[1] + offsetY
        elif self.__referencePoint[1] == 'BOTTOM':
            y = self.__screenSize[1] + self.__offset[1] + offsetY
        _logger.debug('%s.setPositionByScreen (%d, %d)', self.className, x, y)
        self.as_setPositionS(x, y)

    def setPositionByCrosshair(self):
        if not self.__wasPopulated:
            return
        if self.__reference != 'CROSSHAIR':
            return
        _logger.debug('%s.setPositionByCrosshair', self.className)
        width, height = self.as_getPanelSizeS()
        _logger.debug('%s.setPositionByCrosshair width=%d, height=%d', self.className, width, height)
        offsetX = offsetY = 0
        halign, valign = self.__align
        if halign == 'RIGHT':
            offsetX = - width
        elif halign == 'CENTER':
            offsetX = - width / 2
        if valign == 'BOTTOM':
            offsetY = - height
        elif valign == 'CENTER':
            offsetY = - height / 2
        x = self.__crosshairPosition[0] + self.__crosshairOffset[self.__crosshairView][0] + offsetX
        y = self.__crosshairPosition[1] + self.__crosshairOffset[self.__crosshairView][1] + offsetY
        _logger.debug('%s.setPositionByCrosshair view=%s, crosshairOffset=(%d, %d)', self.className, self.__crosshairView, self.__crosshairOffset[self.__crosshairView][0], self.__crosshairOffset[self.__crosshairView][1])
        _logger.debug('%s.setPositionByCrosshair crosshair=(%d, %d), panel=(%d, %d)', self.className, self.__crosshairPosition[0], self.__crosshairPosition[1], x, y)
        self.as_setPositionS(x, y)


PANEL_VIEW_SETTINGS = ViewSettings(
    PANEL_VIEW_ALIAS,
    PanelView,
    PANEL_VIEW_SWF_FILE_PATH,
    ViewTypes.WINDOW,
    None,
    ScopeTemplates.DEFAULT_SCOPE
)
