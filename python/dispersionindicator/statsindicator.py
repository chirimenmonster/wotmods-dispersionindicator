
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
        self.__statsTable = {}
        for key in config['items']:
            statDef = config['statsDefs'].get(key, None)
            if statDef is None:
                continue
            self.__statsTable[key] = desc = {}
            for tag in ['status', 'title', 'label', 'unit', 'format']:
                if tag in statDef:
                    desc[tag] = statDef[tag]
            factor = statDef.get('factor', None)
            if isinstance(factor, str) or isinstance(factor, unicode):
                factor = CONSTANT.get(factor, None)
            if factor is not None:
                desc['factor'] = factor
        
    @property
    def vehicleStats(self):
        return self.__vehicleStats

    def getStatus(self, name):
        desc = self.__statsTable.get(name, None)
        statusName = desc['status'] if desc is not None else name
        try:
            value = getattr(self.__vehicleStats, statusName, None)
        except AttributeError:
            _logger.error('%s.getStatus: unknown status name "%s"', self.className, statusName)
            return None
        if value is None:
            return None
        if desc is not None and 'factor' in desc:
            value *= desc['factor']
        return value

    def getStatusAsText(self, name):
        desc = self.__statsTable.get(name, {})
        template = desc.get('format', None)
        value = self.getStatus(name)
        if value is None:
            return ''
        if template is not None:
            try:
                text = template.format(value)
            except:
                _logger.error('%s.getStatusAsText: "%s"', self.className, json.dumps(desc))
                text = str(value)
        else:
            text = str(value)
        return text

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
        self.__visibleControl = config['style'].get('visibleControl', None)
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
        self.acceptEvents = config.get('events', [])
        appLoader = dependency.instance(IAppLoader)
        app = appLoader.getDefBattleApp()
        if not app:
            _logger.info('%s.__init__: not found app', self.className)
            return
        app.loadView(SFViewLoadParams(PANEL_VIEW_ALIAS, self.name), config=self.__guiSettings)
        pyEntity = app.containerManager.getViewByKey(ViewKey(PANEL_VIEW_ALIAS, self.name))
        self.__pyEntity = weakref.proxy(pyEntity)

    def start(self):
        super(StatsIndicator, self).start()
        for conf in self.__guiSettings['stats']:
            self.__setIndicatorValue(conf['name'], '')
        if not self.__visibleControl:
            self.__pyEntity.setVisible(True)

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
        for conf in self.__guiSettings['stats']:
            name = conf['name']
            text = self.getStatusAsText(name)
            self.__setIndicatorValue(name, text)
        if self.__visibleControl:
            if getattr(self.vehicleStats, self.__visibleControl, None):
                self.__pyEntity.setVisible(True)
            else:
                self.__pyEntity.setVisible(False)


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
        #_logger.debug('%s.onEvent: receive event: %s, %s', self.className, reason['eventTime'], reason['eventName'])
        if reason['eventName'] not in self.acceptEvents:
            return
        self.update()
