
import logging
import json
import weakref
from functools import partial

import GUI
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.framework.entities.View import ViewKey

from mod_constants import MOD, CONSTANT, CROSSHAIR_VIEW_SYMBOL
from view.panelview import PANEL_VIEW_ALIAS

_logger = logging.getLogger(MOD.NAME)

SWF_FILE = 'IndicatorPanel.swf'
SWF_PATH = '${flash_dir}'


class StatsIndicatorMeta(object):
    onEvent = None

    def __init__(self, collector):
        self.className = self.__class__.__name__
        self.__vehicleStats = collector
        
    @property
    def vehicleStats(self):
        return self.__vehicleStats

    def getStatus(self, name, factor):
        return getattr(self.vehicleStats, name, 0.0) * factor

    def start(self):
        pass

    def stop(self):
        pass

    def changeView(self, crosshairViewID):
        pass

    def updateScreenPosition(self, width, height):
        pass

    def updateCrosshairPosition(self, x, y):
        pass

    def update(self):
        pass


class StatsIndicator(StatsIndicatorMeta):
    def __init__(self, config, collector, name):
        super(StatsIndicator, self).__init__(collector)
        _logger.info('%s.__init__: "%s"', self.className, name)
        self.name = name
        self.statsdefs = config['statsDefs']
        self.__guiSettings = {}
        self.__guiSettings['style'] = config['style']
        self.__guiSettings['stats'] = []
        self.__statsSource = {}
        for key in config['items']:
            print 'key: ', key
            setting = self.statsdefs[key]
            factor = setting['factor']
            if isinstance(factor, str) or isinstance(factor, unicode):
                factor = CONSTANT.get(factor, 1.0)
            self.__guiSettings['stats'].append({
                'name':         key,
                'label':        setting['title'],
                'unit':         setting['unit']
            })
            self.__statsSource[key] = {
                'func':         partial(self.getStatus, key, factor),
                'format':       setting['format']
            }
        appLoader = dependency.instance(IAppLoader)
        app = appLoader.getDefBattleApp()
        if not app:
            _logger.info('%s.__init__: not found app', self.className)
            return
        app.loadView(SFViewLoadParams(PANEL_VIEW_ALIAS, name), config=self.__guiSettings)
        pyEntity = app.containerManager.getViewByKey(ViewKey(PANEL_VIEW_ALIAS, name))
        pyEntity.setVisible(True)
        self.__pyEntity = weakref.proxy(pyEntity)

    def start(self):
        _logger.info('%s.start: "%s"', self.className, self.name)
        for name, config in self.__statsSource.items():
            text = config['format'].format(0)
            self.__setIndicatorValue(name, text)

    def stop(self):
        _logger.info('%s.stop: "%s"', self.className, self.name)
        try:
            self.__pyEntity.setVisible(False)
        except weakref.ReferenceError:
            pass

    def __setIndicatorValue(self, name, value):
        try:
            self.__pyEntity.as_setValueS(name, value)
        except weakref.ReferenceError:
            pass

    def update(self):
        for name, config in self.__statsSource.items():
            text = config['format'].format(config['func']())
            self.__setIndicatorValue(name, text)

    def updateScreenPosition(self, width, height):
        self.__screenSize = [ width, height ]
        try:
            self.__pyEntity.setScreenResolution(width, height)
            self.__pyEntity.setPositionByScreen()
        except weakref.ReferenceError:
            pass

    def updateCrosshairPosition(self, x, y):
        self.__crosshairPosition = [ x, y ]
        try:
            self.__pyEntity.setCrosshairPosition(x, y)
            self.__pyEntity.setPositionByCrosshair()
        except weakref.ReferenceError:
            pass

    def changeView(self, viewID):
        self.__crosshairView = viewID
        try:
            self.__pyEntity.setCrosshairView(viewID)
        except weakref.ReferenceError:
            pass
