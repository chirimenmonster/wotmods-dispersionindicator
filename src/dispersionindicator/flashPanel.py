
import weakref
import BigWorld
import GUI
from gui.app_loader import g_appLoader
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.framework.entities.View import ViewKey

from mod_constants import MOD_NAME, CONSTANT, CROSSHAIR_VIEW_SYMBOL
from view.panelview import PANEL_VIEW_ALIAS

SWF_FILE = 'IndicatorPanel.swf'
SWF_PATH = '${flash_dir}'

class IndicatorFlashText(object):
    def __init__(self, config, stats, name):
        self.setPanelStyle(config, stats, name)

    def setPanelStyle(self, config, stats, name):
        self.stats = stats
        self.name = name
        self.__style = style = config['style']
        self.referencePoint = style['referencePoint']
        self.horizontalAnchor = style['horizontalAnchor']
        self.verticalAnchor = style['verticalAnchor']
        self.screenOffset = style['screenOffset']
        self.crosshairOffset = { id:style.get('crosshairOffset_' + symbol, style['crosshairOffset']) for id, symbol in CROSSHAIR_VIEW_SYMBOL.items() }
        self.statsdefs = config['statsDefs']

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
    
    def init(self):
        BigWorld.logInfo(MOD_NAME, 'flashText.init: "{}"'.format(self.name), None)
        name = self.name
        app = g_appLoader.getDefBattleApp()
        if not app:
            BigWorld.logInfo(MOD_NAME, 'not found app', None)
            return
        app.loadView(SFViewLoadParams(PANEL_VIEW_ALIAS, name))
        pyEntity = app.containerManager.getViewByKey(ViewKey(PANEL_VIEW_ALIAS, name))
        if not pyEntity:
            BigWorld.logInfo(MOD_NAME, 'not found ViewKey: "{}"'.format(ViewKey(PANEL_VIEW_ALIAS, name)), None)
            self.__pyEntity = None
            return
        pyEntity.setConfig(self.__config, self.__style)
        self.__pyEntity = weakref.proxy(pyEntity)
        #self.__pyEntity.as_createPanelS(self.__config, self.__style)
        self.__viewID = 0


    def start(self):
        BigWorld.logInfo(MOD_NAME, 'flashText.start: "{}"'.format(self.name), None)
        for config in self.__config:
            name = config['name']
            text = config['format'].format(0)
            self.__pyEntity.as_setValueS(name, text)
        self.updateScreenPosition()
        #self.__pyEntity.active(True)

    def stop(self):
        BigWorld.logInfo(MOD_NAME, 'flashText.stop: "{}"'.format(self.name), None)
        #self.__pyEntity.active(False)
   
    def _getIndicatorSize(self):
        BigWorld.logInfo(MOD_NAME, 'flashText.getIndicatorSize', None)
        width, height = self.__pyEntity.getPanelSize()
        BigWorld.logInfo(MOD_NAME, 'flashText.getIndicatorSize: {}, {}'.format(width, height), None)
        return width, height
    
    def _setIndicatorPosition(self, x, y):
        self.__pyEntity.as_setPositionS(int(x), int(y))

    def _setIndicatorValue(self, name, value):
        self.__pyEntity.as_setValueS(name, value)

    def update(self):
        data = getattr(self.stats, 'aimingTimeConverging', 0.0)
        for config in self.__config:
            name = config['name']
            text = config['format'].format(config['func']())
            self._setIndicatorValue(name, text)

    def updateScreenPosition(self):
        BigWorld.logInfo(MOD_NAME, 'flashText.updateScreenPosition', None)
        width, height = self._getIndicatorSize()
        refPoint = self.referencePoint.split('_')
        if refPoint[0] != 'SCREEN':
            return
        if len(refPoint) == 2 and refPoint[1] == 'CENTER':
            refPoint.append('CENTER')
        offsetX = offsetY = 0
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
        BigWorld.logInfo(MOD_NAME, 'flashText.updatePosition ({}, {})'.format(x, y), None)
        self._setIndicatorPosition(x, y)

    def updateCrosshairPosition(self, x, y):
        if self.referencePoint != 'CROSSHAIR':
            return
        BigWorld.logInfo(MOD_NAME, 'flashText.updateCrosshairPosition ({}, {})'.format(x, y), None)
        offsetX = offsetY = 0
        width, height = self._getIndicatorSize()
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
        BigWorld.logInfo(MOD_NAME, 'flashText.updatePosition ({}, {})'.format(x, y), None)
        self._setIndicatorPosition(x, y)

    def changeView(self, viewID):
        self.__viewID = viewID
        return
