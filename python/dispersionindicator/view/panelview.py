
import logging
import BigWorld
from gui.Scaleform.framework import ViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.framework.entities.View import View
from gui.battle_control.battle_constants import CROSSHAIR_VIEW_ID

MOD_NAME = '${name}'

PANEL_VIEW_ALIAS = 'DispersionIndicatorPanel'
PANEL_VIEW_SWF_FILE_PATH = 'dispersionindicator/IndicatorPanel.swf'

for name in [ 'gui.Scalform.framework.entities.View', 'gui.Scaleform.Flash' ]:
    logging.getLogger(name).setLevel(logging.DEBUG)
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class PanelView(View):
    def __init__(self, *args, **kwargs):
        super(PanelView, self).__init__(*args, **kwargs)
        self.__reference = None
        self.__crosshairView = CROSSHAIR_VIEW_ID.UNDEFINED

    def as_setConfigS(self, settings):
        BigWorld.logInfo(MOD_NAME, 'PanelView: as_setConfigS', None)
        self.flashObject.as_setConfig(settings)

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

    def setReferencePoint(self, referencePoint, align, offset, crosshairOffset):
        BigWorld.logInfo(MOD_NAME, 'PanelView: setReferencePoint: {}'.format(referencePoint), None)
        r = referencePoint.split('_')
        if r[0] == 'SCREEN':
            if len(r) == 2 and r[1] == 'CENTER':
                r.append('CENTER')
            self.__reference = r[0]
            self.__referencePoint = [ r[1], r[2] ]
        elif r[0] == 'CROSSHAIR':
            self.__reference = r[0]
        else:
            raise 'unknown referncePoint: {}'.format(referencePoint)
        self.__align = align
        self.__offset = offset
        self.__crosshairOffset = crosshairOffset

    def setScreenResolution(self, width, height):
        self.__screenSize = [ width, height ]

    def setCrosshairPosition(self, x, y):
        self.__crosshairPosition = [ x, y ]

    def setCrosshairView(self, crosshairView):
        self.__crosshairView = crosshairView

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
