
import json
import weakref
from functools import partial

import BigWorld
import GUI
from gui.app_loader import g_appLoader
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.framework.entities.View import ViewKey

from mod_constants import MOD_NAME, CONSTANT, CROSSHAIR_VIEW_SYMBOL
from view.panelview import PANEL_VIEW_ALIAS

SWF_FILE = 'IndicatorPanel.swf'
SWF_PATH = '${flash_dir}'


class StatsIndicatorMeta(object):
    def __init__(self, vehicleStats):
        self.className = type(self)
        self.__vehicleStats = vehicleStats
        
    @property
    def vehicleStats(self):
        return self.__vehicleStats

    def getStatus(self, name, factor):
        return getattr(self.vehicleStats, name, 0.0) * facor

    def start(self):
        pass

    def stop(self):
        pass

    def changeView(self, crosshairViewID):
        pass

    def updateScreenPositoion(self, width, height):
        pass

    def updateCrosshairPosition(self, x, y):
        pass

    def update(self):
        pass


class StatsIndicator(StatsIndicatorMeta):
    def __init__(self, config, vehicleStats, name):
        super(StatsIndicator, self).__init__(vehicleStats)
        self.name = name
        self.statsdefs = config['statsDefs']
        self.__guiSettings = {}
        self.__guiSettings['style'] = config['style']
        self.__guiSettings['stats'] = {}
        self.__statsSource = {}
        for key in config['items']:
            setting = self.statsdefs[key]
            factor = setting['factor']
            if isinstance(factor, str) or isinstance(factor, unicode):
                factor = CONSTANT.get(factor, 1.0)
            self.__guiSettings['stats'].append({
                'name':         setting['name'],
                'label':        setting['title'],
                'unit':         setting['unit']
            })
            self.__statsSource[key] = {
                'func':         partial(self.getStatus, setting['name'], factor),
                'format':       setting['template']
            }
        app = g_appLoader.getDefBattleApp()
        if not app:
            BigWorld.logInfo(MOD_NAME, '{}.init: not found app'.format(self.className), None)
            return
        app.loadView(SFViewLoadParams(PANEL_VIEW_ALIAS, name), settings=self.__guiSettings)
        pyEntity = app.containerManager.getViewByKey(ViewKey(PANEL_VIEW_ALIAS, name))
        self.__pyEntity = weakref.ref(pyEntity)

    def start(self):
        BigWorld.logInfo(MOD_NAME, '{}.start: "{}"'.format(self.className, self.name), None)
        for name, config in self.__statsSource.items():
            text = config['format'].format(0)
            self._setIndicatorValue(name, text)

    def stop(self):
        BigWorld.logInfo(MOD_NAME, '{}.stop: "{}"'.format(self.className, self.name), None)
        pyEntity = self.__pyEntity()
        if pyEntity is not None:
            pyEntity.setVisible(False)
   
    def _setIndicatorValue(self, name, value):
        pyEntity = self.__pyEntity()
        if pyEntity is not None:
            pyEntity.as_setValueS(name, value)

    def update(self):
        for name, config in self.__statsSource.items():
            text = config['format'].format(config['func']())
            self._setIndicatorValue(name, text)
    
    def updateScreenPosition(self, width, height):
        self.__screenSize = [ width, height ]
        pyEntity = self.__pyEntity()
        if pyEntity is not None:
            pyEntity.setScreenResolution(width, height)
            pyEntity.calcPositionByScreen()

    def updateCrosshairPosition(self, x, y):
        self.__crosshairPosition = [ x, y ]
        pyEntity = self.__pyEntity()
        if pyEntity is not None:
            pyEntity.setCrosshairPosition(x, y)
            pyEntity.calcPositionByCrosshair()

    def changeView(self, viewID):
        self.__crosshairView = viewID
        pyEntity = self.__pyEntity()
        if pyEntity is not None:
            pyEntity.setCrosshairView(viewID)
