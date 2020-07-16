
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

    def __init__(self, config, clientStatus):
        self.className = self.__class__.__name__
        self.__vehicleStats = clientStatus
        self.name = config['name']
        _logger.info('%s.__init__: "%s"', self.className, self.name)
        
    @property
    def vehicleStats(self):
        return self.__vehicleStats

    def getStatus(self, name, factor=None):
        value = getattr(self.vehicleStats, name, None)
        if value is None:
            result = ''
        else:
            if factor is not None:
                result = value * factor
            else:
                result = value
        return result

    def start(self):
        _logger.info('%s.start: "%s"', self.className, self.name)

    def stop(self):
        _logger.info('%s.stop: "%s"', self.className, self.name)

    def changeView(self, crosshairViewID):
        pass

    def updateScreenPosition(self, width, height):
        pass

    def updateCrosshairPosition(self, x, y):
        pass

    def update(self):
        pass


class StatsIndicator(StatsIndicatorMeta):
    def __init__(self, config, clientStatus):
        super(StatsIndicator, self).__init__(config, clientStatus)
        self.statsdefs = config['statsDefs']
        self.__guiSettings = {}
        self.__guiSettings['style'] = config['style']
        self.__guiSettings['stats'] = []
        self.__statsSource = {}
        for key in config['items']:
            setting = self.statsdefs[key]
            self.__guiSettings['stats'].append({
                'name':         key,
                'label':        setting.get('title', ''),
                'unit':         setting.get('unit', ''),
                'statWidth':    setting.get('statWidth', config['style']['statWidth']),
                'statAlign':    setting.get('statAlign', config['style']['statAlign']),
                'lineAlign':    setting.get('lineAlign', config['style']['lineAlign'])
            })
            factor = setting.get('factor', None)
            if isinstance(factor, str) or isinstance(factor, unicode):
                factor = CONSTANT.get(factor, 1.0)
            self.__statsSource[key] = {
                'func':         partial(self.getStatus, key, factor),
                'format':       setting.get('format', '{}')
            }
        self.acceptEvents = config.get('events', [])
        appLoader = dependency.instance(IAppLoader)
        app = appLoader.getDefBattleApp()
        if not app:
            _logger.info('%s.__init__: not found app', self.className)
            return
        app.loadView(SFViewLoadParams(PANEL_VIEW_ALIAS, self.name), config=self.__guiSettings)
        pyEntity = app.containerManager.getViewByKey(ViewKey(PANEL_VIEW_ALIAS, self.name))
        pyEntity.setVisible(True)
        self.__pyEntity = weakref.proxy(pyEntity)

    def start(self):
        super(StatsIndicator, self).start()
        for name, config in self.__statsSource.items():
            self.__setIndicatorValue(name, '')

    def stop(self):
        super(StatsIndicator, self).stop()
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
            value = config['func']()
            if value is not None and value != '':
                text = config['format'].format(value)
            else:
                text = ''
            self.__setIndicatorValue(name, text)

    def updateScreenPosition(self, width, height):
        self.__screenSize = [ width, height ]
        try:
            self.__pyEntity.setScreenResolution(width, height)
            self.__pyEntity.setPositionByScreen()
        except weakref.ReferenceError:
            pass

    def updateCrosshairPosition(self, x, y):
        _logger.debug('%s.updateCrosshairPosition: [%s, %s]', self.className, x, y)
        self.__crosshairPosition = [ x, y ]
        try:
            self.__pyEntity.setCrosshairPosition(x, y)
            self.__pyEntity.setPositionByCrosshair()
        except weakref.ReferenceError:
            _logger.warning('%s.updateCrosshairPosition: ReferenceError: not found PanelView', self.className)
            pass

    def changeView(self, viewID):
        self.__crosshairView = viewID
        try:
            self.__pyEntity.setCrosshairView(viewID)
        except weakref.ReferenceError:
            pass

    def onEvent(self, reason):
        if reason['eventName'] not in self.acceptEvents:
            return
        self.update()
