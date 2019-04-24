
import json
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

class StatsIndicator(object):
    className = 'StatsIndicator'

    def __init__(self, config, stats, name):
        self.setPanelStyle(config, stats, name)

    def setPanelStyle(self, config, stats, name):
        self.__stats = stats
        self.name = name
        style = config['style']
        self.referencePoint = style['referencePoint']
        self.horizontalAnchor = style['horizontalAnchor']
        self.verticalAnchor = style['verticalAnchor']
        self.screenOffset = style['screenOffset']
        self.crosshairOffset = { id:style.get('crosshairOffset_' + symbol, style['crosshairOffset']) for id, symbol in CROSSHAIR_VIEW_SYMBOL.items() }
        self.statsdefs = config['statsDefs']
        self.__guiSettings = { 'style': style, 'stats': [] }
        self.__statsSource = {}
        for key in config['items']:
            setting = self.statsdefs[key]
            statsName = setting['status']
            factor = setting['factor']
            template = setting['format']
            if isinstance(factor, str) or isinstance(factor, unicode):
                factor = CONSTANT.get(factor, 1.0)
            self.__guiSettings['stats'].append({
                'name':         key,
                'label':        setting['title'],
                'unit':         setting['unit']
            })
            self.__statsSource[key] = {
                'func':         lambda n=statsName, f=factor, s=self.__stats: getattr(s, n, 0.0) * f,
                'format':       template
            }
    
    def init(self):
        BigWorld.logInfo(MOD_NAME, '{}.init: "{}"'.format(self.className, self.name), None)
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
        pyEntity.onCreate += self.setConfig
        self.__pyEntity = weakref.proxy(pyEntity)

    def setConfig(self, pyEntity):
        BigWorld.logInfo(MOD_NAME, '{}.setConfig: "{}"'.format(self.className, self.name), None)
        #print json.dumps(self.__guiSettings, indent=2)
        pyEntity.as_setConfigS(self.__guiSettings)
        align = [ self.horizontalAnchor, self.verticalAnchor ]
        pyEntity.setReferencePoint(self.referencePoint, align, self.screenOffset, self.crosshairOffset)
        pyEntity.setVisible(False)

    def start(self):
        BigWorld.logInfo(MOD_NAME, '{}.start: "{}"'.format(self.className, self.name), None)
        for name, config in self.__statsSource.items():
            text = config['format'].format(0)
            self._setIndicatorValue(name, text)
        self.__pyEntity.setVisible(True)

    def stop(self):
        BigWorld.logInfo(MOD_NAME, '{}.stop: "{}"'.format(self.className, self.name), None)
        try:
            self.__pyEntity.setVisible(False)
        except weakref.ReferenceError:
            pass
   
    def _setIndicatorValue(self, name, value):
        self.__pyEntity.as_setValueS(name, value)

    def update(self):
        for name, config in self.__statsSource.items():
            text = config['format'].format(config['func']())
            self._setIndicatorValue(name, text)
    
    def updateScreenPosition(self, width, height):
        self.__screenSize = [ width, height ]
        if self.__pyEntity:
            self.__pyEntity.setScreenResolution(width, height)
            self.__pyEntity.calcPositionByScreen()

    def updateCrosshairPosition(self, x, y):
        self.__crosshairPosition = [ x, y ]
        if self.__pyEntity:
            self.__pyEntity.setCrosshairPosition(x, y)
            self.__pyEntity.calcPositionByCrosshair()

    def changeView(self, viewID):
        self.__crosshairView = viewID
        if self.__pyEntity:
            self.__pyEntity.setCrosshairView(viewID)
