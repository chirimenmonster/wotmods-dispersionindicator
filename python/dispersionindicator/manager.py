
import logging
import BigWorld
import GUI
from constants import ARENA_PERIOD
from gui import g_guiResetters
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader, GuiGlobalSpaceID
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.shared import g_eventBus, events
from gui.shared.utils.TimeInterval import TimeInterval
from gui.app_loader.settings import APP_NAME_SPACE
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, CROSSHAIR_VIEW_ID

from mod_constants import MOD, CONSTANT, CROSSHAIR_VIEW_SYMBOL, ARENA_PERIOD_SYMBOL, GUI_GLOBAL_SPACE_SYMBOL
from statscollector import g_statscollector
from statsindicator import StatsIndicator
from statslogger import StatsLogger
from eventlogger import EventLogger

_logger = logging.getLogger(MOD.NAME)

class IndicatorManager(object):
    def __init__(self, config):
        self.__config = config
        self.__panels = []
        self.__stats = g_statscollector
        self.__isSetHandler = False
        self.__visible = False
        self.__crosshairPosition = [ 0, 0 ]
        self.__onShoot = []
        self.__onShot = []
        self.__onShotResult = []
        interval = config['common']['updateInterval']
        self.__timeInterval = TimeInterval(interval, self, 'onWatchStats')
        g_eventBus.addListener(events.AppLifeCycleEvent.INITIALIZED, self.onAppInitialized)
        g_eventBus.addListener(events.AppLifeCycleEvent.DESTROYED, self.onAppDestroyed)
        appLoader = dependency.instance(IAppLoader)
        appLoader.onGUISpaceEntered += self.onGUISpaceEntered
        appLoader.onGUISpaceLeft += self.onGUISpaceLeft

    def initPanel(self):
        _logger.info('initPanel')
        self.addHandler()
        self.__panels = []
        for name, paneldef in sorted(self.__config['panels'].items(), key=lambda x:x[0]):
            self.__panels.append(StatsIndicator(paneldef, self.__stats, name))
        if 'logs' in self.__config:
            self.__panels.append(StatsLogger(self.__config['logs'], self.__stats))
        if 'eventLog' in self.__config or True:
            panel = EventLogger(None, self.__stats)
            self.__panels.append(panel)
            self.__onShot = lambda p=panel: p.onEvent('shot')
            self.__onShoot = lambda p=panel: p.onEvent('shoot')
            self.__onShotResult = lambda p=panel: p.onEvent('shotResult')
            g_statscollector.onShot = lambda : self.__onShot()
            g_statscollector.onShoot = lambda : self.__onShot()
            g_statscollector.onShotResult = lambda : self.__onShotResult()
        self.updateScreenPosition()
        self.updateCrosshairPosition()

    def finiPanel(self):
        _logger.info('finiPanel')
        self.stopIntervalTimer()
        self.invisiblePanel()
        self.removeHandler()
        self.__panels = []

    def addHandler(self):
        if self.__isSetHandler:
            return
        self.__isSetHandler = True
        arena = BigWorld.player().arena
        arena.onPeriodChange += self.onArenaPeriodChange
        session = dependency.instance(IBattleSessionProvider)
        ctl = session.shared.vehicleState
        ctl.onVehicleStateUpdated += self.onVehicleStateUpdated
        ctl = session.shared.crosshair
        ctl.onCrosshairViewChanged += self.onCrosshairViewChanged
        ctl.onCrosshairPositionChanged += self.onCrosshairPositionChanged
        self.__crosshairPosition = list(ctl.getScaledPosition())
        g_guiResetters.add(self.onScreenResolutionChanged)
    
    def removeHandler(self):
        if not self.__isSetHandler:
            return
        self.__isSetHandler = False
        player = BigWorld.player()
        if player:
            arena = player.arena
            if arena:
                arena.onPeriodChange -= self.onArenaPeriodChange
        session = dependency.instance(IBattleSessionProvider)
        ctl = session.shared.vehicleState
        if ctl:
            ctl.onVehicleStateUpdated -= self.onVehicleStateUpdated
        ctl = session.shared.crosshair
        if ctl:
            ctl.onCrosshairViewChanged -= self.onCrosshairViewChanged
            ctl.onCrosshairPositionChanged -= self.onCrosshairPositionChanged
        g_guiResetters.remove(self.onScreenResolutionChanged)

    def visiblePanel(self):
        if self.__visible:
            return
        self.__visible = True
        _logger.info('panel.start')
        for panel in self.__panels:
            panel.start()

    def invisiblePanel(self):
        if not self.__visible:
            return
        self.__visible = False
        _logger.info('panel.stop')
        for panel in self.__panels:
            panel.stop()

    def startIntervalTimer(self):
        if not self.__timeInterval.isStarted():
            _logger.info('TimeInterval: start')
            self.__timeInterval.start()

    def stopIntervalTimer(self):
        if self.__timeInterval.isStarted():
            _logger.info('TimeInterval: stop')
            self.__timeInterval.stop()

    def changeView(self, viewID):
        _logger.debug('changeView: %s', CROSSHAIR_VIEW_SYMBOL[viewID])
        for panel in self.__panels:
            panel.changeView(viewID)

    def updateScreenPosition(self):
        width, height = GUI.screenResolution()
        _logger.debug('updateScreenPosition: (%d, %d)', width, height)
        for panel in self.__panels:
            panel.updateScreenPosition(width, height)

    def updateCrosshairPosition(self):
        x, y = self.__crosshairPosition
        _logger.debug('updateCrosshairPosition: (%d, %d)', x, y)
        for panel in self.__panels:
            panel.updateCrosshairPosition(x, y)

    def onAppInitialized(self, event):
        if event.ns != APP_NAME_SPACE.SF_BATTLE:
            return
        _logger.info('AppLifeCycleEvent.INITIALIZED: SF_BATTLE')
        #self.initPanel()

    def onAppDestroyed(self, event):
        if event.ns != APP_NAME_SPACE.SF_BATTLE:
            return
        _logger.info('AppLifeCycleEvent.DESTROYED: SF_BATTLE')
        self.finiPanel()

    def onGUISpaceEntered(self, spaceID):
        if spaceID != GuiGlobalSpaceID.BATTLE:
            return
        _logger.info('onGUISpaceEnterd: %s', GUI_GLOBAL_SPACE_SYMBOL[spaceID])
        self.initPanel()
    
    def onGUISpaceLeft(self, spaceID):
        if spaceID != GuiGlobalSpaceID.BATTLE:
            return
        _logger.info('onGUISpaceLeft: %s', GUI_GLOBAL_SPACE_SYMBOL[spaceID])
        self.finiPanel()

    def onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        _logger.info('onArenaPeriodChange: %s', ARENA_PERIOD_SYMBOL[period])
        if period == ARENA_PERIOD.PREBATTLE:
            self.visiblePanel()
        elif period == ARENA_PERIOD.BATTLE:
            self.visiblePanel()
            self.startIntervalTimer()
        elif period == ARENA_PERIOD.AFTERBATTLE:
            self.stopIntervalTimer()
            self.invisiblePanel()

    def onVehicleStateUpdated(self, stateID, value):
        if stateID == VEHICLE_VIEW_STATE.DESTROYED:
            _logger.info('onVehicleStateUpdated: VEHICLE_VIEW_STATE.DESTROYED')
            self.stopIntervalTimer()
            self.invisiblePanel()
    
    def onScreenResolutionChanged(self):
        width, height = GUI.screenResolution()
        _logger.debug('onScreenResolutionChanged: (%d, %d)', width, height)
        for panel in self.__panels:
            panel.updateScreenPosition(width, height)

    def onCrosshairViewChanged(self, viewID):
        _logger.debug('crosshairViewChanged: %s', CROSSHAIR_VIEW_SYMBOL[viewID])
        self.changeView(viewID)

    def onCrosshairPositionChanged(self, x, y):
        _logger.debug('onCrosshairPositionChanged: (%d, %d)', x, y)
        self.__crosshairPosition = [ x, y ]
        for panel in self.__panels:
            panel.updateCrosshairPosition(x, y)

    def onWatchStats(self):
        for panel in self.__panels:
            panel.update()

    def onEventShoot(self):
        self.__onShoot()

    def onEventShot(self):
        self.__onShot()

    def onEventShotResult(self):
        self.__onShotResult()
