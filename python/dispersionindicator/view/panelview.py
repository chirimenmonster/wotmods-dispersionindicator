
import logging
import BigWorld
from gui.Scaleform.framework import ViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.framework.entities.View import View
from gui.battle_control.battle_constants import CROSSHAIR_VIEW_ID

from mod_constants import MOD_NAME, CONSTANT, CROSSHAIR_VIEW_SYMBOL

PANEL_VIEW_ALIAS = 'DispersionIndicatorPanel'
PANEL_VIEW_SWF_FILE_PATH = 'dispersionindicator/IndicatorPanel.swf'

for name in [ 'gui.Scalform.framework.entities.View', 'gui.Scaleform.Flash' ]:
    logging.getLogger(name).setLevel(logging.DEBUG)
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class PanelView(View):
    def __init__(self, settings=None, *args, **kwargs):
        super(PanelView, self).__init__(*args, **kwargs)
        self.__settings = settings
        style = settings['style']
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
        self.__offset = style['offset']
        self.__crosshairOffset = {}
        for id, symbol in CROSSHAIR_VIEW_SYMBOL.items():
            self.__crosshairOffset[id] = style.get('crosshairOffset_' + symbol, style['crosshairOffset'])
        self.__crosshairView = CROSSHAIR_VIEW_ID.UNDEFINED
        self.onCreate += self.setConfig

    def setConfig(self):
        BigWorld.logInfo(MOD_NAME, 'PanelView: setConfig', None)
        self.flashObject.as_setConfig(self.__settings)
        self.calcPosition()

    def as_setPositionS(self, x, y):
        #BigWorld.logInfo(MOD_NAME, 'PanelView: as_setPositionS: ({}, {})'.format(x, y), None)
        self.flashObject.as_setPosition(x, y)

    def as_setValueS(self, name, value):
        #BigWorld.logInfo(MOD_NAME, 'PanelView: as_setValueS: ({}, {})'.format(name, value), None)
        self.flashObject.as_setValue(name, value)

    def as_getPanelSizeS(self):
        #BigWorld.logInfo(MOD_NAME, 'PanelView: as_getPanelSizeS', None)
        result = self.flashObject.as_getPanelSize()
        return result.width, result.height

    def setScreenResolution(self, width, height):
        self.__screenSize = [ width, height ]

    def setCrosshairPosition(self, x, y):
        self.__crosshairPosition = [ x, y ]

    def setCrosshairView(self, crosshairView):
        self.__crosshairView = crosshairView

    def setVisible(self, isVisible):
        BigWorld.logInfo(MOD_NAME, 'PanelView: setVisible: {}'.format(isVisible), None)
        self.flashObject.visible = isVisible

    def calcPosition(self):
        BigWorld.logInfo(MOD_NAME, 'PanelView: calcPosition: {}'.format(self.__reference), None)
        if self.__reference == 'SCREEN':
            self.calcPositionByScreen()
        elif self.__reference == 'CROSSHAIR':
            self.calcPositionByCrosshair()

    def calcPositionByScreen(self):
        if self.__reference != 'SCREEN':
            return
        BigWorld.logInfo(MOD_NAME, 'PanelView: calcPositionByScreen: {}'.format(self.__align), None)
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
        #BigWorld.logInfo(MOD_NAME, '{}.updatePosition ({}, {})'.format(self.className, x, y), None)
        self.as_setPositionS(x, y)

    def calcPositionByCrosshair(self):
        if self.__reference != 'CROSSHAIR':
            return
        BigWorld.logInfo(MOD_NAME, 'PanelView: _calcPositionByCrosshair', None)
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
        x = self.__crosshairPosition[0] + self.__crosshairOffset[self.__crosshairView][0] + offsetX
        y = self.__crosshairPosition[1] + self.__crosshairOffset[self.__crosshairView][1] + offsetY
        #BigWorld.logInfo(MOD_NAME, '{}.updatePosition ({}, {})'.format(self.className, x, y), None)
        self.as_setPositionS(x, y)


PANEL_VIEW_SETTINGS = ViewSettings(
    PANEL_VIEW_ALIAS,
    PanelView,
    PANEL_VIEW_SWF_FILE_PATH,
    ViewTypes.WINDOW,
    None,
    ScopeTemplates.DEFAULT_SCOPE
)
