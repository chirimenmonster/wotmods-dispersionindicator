
import BigWorld
import GUI
from constants import ARENA_PERIOD
from gui import g_guiResetters
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.shared import g_eventBus, events
from gui.shared.utils.TimeInterval import TimeInterval
from gui.app_loader import g_appLoader
from gui.app_loader.settings import APP_NAME_SPACE, GUI_GLOBAL_SPACE_ID
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, CROSSHAIR_VIEW_ID

from mod_constants import MOD_NAME, CONSTANT, CROSSHAIR_VIEW_SYMBOL, ARENA_PERIOD_SYMBOL
from statscollector import g_statscollector
from statsindicator import StatsIndicator
from statslogger import StatsLogger


class IndicatorManager(object):
    def __init__(self, config):
        self.__config = config
        self.__panels = []
        self.__stats = g_statscollector
        self.__isSetHandler = False
        self.__visible = False
        self.__crosshairPosition = [ 0, 0 ]
        interval = config['common']['updateInterval']
        self.__timeInterval = TimeInterval(interval, self, 'onWatchStats')
        g_eventBus.addListener(events.AppLifeCycleEvent.INITIALIZED, self.onAppInitialized)
        g_eventBus.addListener(events.AppLifeCycleEvent.DESTROYED, self.onAppDestroyed)
        g_appLoader.onGUISpaceEntered += self.onGUISpaceEntered
        g_appLoader.onGUISpaceLeft += self.onGUISpaceLeft

    def initPanel(self):
        BigWorld.logInfo(MOD_NAME, 'initPanel', None)
        self.addHandler()
        for name, paneldef in self.__config['panels'].items():
            self.__panels.append(StatsIndicator(paneldef, self.__stats, name))
        if 'logs' in self.__config:
            self.__panels.append(StatsLogger(self.__config['logs'], self.__stats))
        self.updateScreenPosition()
        self.updateCrosshairPosition()

    def finiPanel(self):
        BigWorld.logInfo(MOD_NAME, 'finiPanel', None)
        self.stopIntervalTimer()
        self.invisiblePanel()
        self.removeHandler()
        self._panels = []

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
        BigWorld.logInfo(MOD_NAME, 'panel.start', None)
        for panel in self.__panels:
            panel.start()

    def invisiblePanel(self):
        if not self.__visible:
            return
        self.__visible = False
        BigWorld.logInfo(MOD_NAME, 'panel.stop', None)
        for panel in self.__panels:
            panel.stop()

    def startIntervalTimer(self):
        if not self.__timeInterval.isStarted():
            BigWorld.logInfo(MOD_NAME, 'TimeInterval: start', None)
            self.__timeInterval.start()

    def stopIntervalTimer(self):
        if self.__timeInterval.isStarted():
            BigWorld.logInfo(MOD_NAME, 'TimeInterval: stop', None)
            self.__timeInterval.stop()

    def changeView(self, viewID):
        #BigWorld.logInfo(MOD_NAME, 'changeView: {}'.format(CROSSHAIR_VIEW_SYMBOL[viewID]), None)
        for panel in self.__panels:
            panel.changeView(viewID)

    def updateScreenPosition(self):
        width, height = GUI.screenResolution()
        #BigWorld.logInfo(MOD_NAME, 'updateScreenPosition: ({}, {})'.format(width, height), None)
        for panel in self.__panels:
            panel.updateScreenPosition(width, height)

    def updateCrosshairPosition(self):
        x, y = self.__crosshairPosition
        #BigWorld.logInfo(MOD_NAME, 'updateCrosshairPosition: ({}, {})'.format(x, y), None)
        for panel in self.__panels:
            panel.updateCrosshairPosition(x, y)

    def onAppInitialized(self, event):
        if event.ns != APP_NAME_SPACE.SF_BATTLE:
            return
        BigWorld.logInfo(MOD_NAME, 'AppLifeCycleEvent.INITIALIZED: SF_BATTLE', None)
        #self.initPanel()

    def onAppDestroyed(self, event):
        if event.ns != APP_NAME_SPACE.SF_BATTLE:
            return
        BigWorld.logInfo(MOD_NAME, 'AppLifeCycleEvent.DESTROYED: SF_BATTLE', None)
        self.finiPanel()

    def onGUISpaceEntered(self, spaceID):
        if spaceID != GUI_GLOBAL_SPACE_ID.BATTLE:
            return
        BigWorld.logInfo(MOD_NAME, 'onGUISpaceEnterd: {}'.format(spaceID), None)
        self.initPanel()
    
    def onGUISpaceLeft(self, spaceID):
        if spaceID != GUI_GLOBAL_SPACE_ID.BATTLE:
            return
        BigWorld.logInfo(MOD_NAME, 'onGUISpaceLeft: {}'.format(spaceID), None)
        self.finiPanel()

    def onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        BigWorld.logInfo(MOD_NAME, 'onArenaPeriodChange: {}'.format(ARENA_PERIOD_SYMBOL[period]), None)
        if period == ARENA_PERIOD.PREBATTLE:
            self.visiblePanel()
        elif period == ARENA_PERIOD.BATTLE:
            self.startIntervalTimer()
        elif period == ARENA_PERIOD.AFTERBATTLE:
            self.stopIntervalTimer()
            self.invisiblePanel()

    def onVehicleStateUpdated(self, stateID, value):
        if stateID == VEHICLE_VIEW_STATE.DESTROYED:
            BigWorld.logInfo(MOD_NAME, 'onVehicleStateUpdated: VEHICLE_VIEW_STATE.DESTROYED', None)
            self.stopIntervalTimer()
            self.invisiblePanel()
    
    def onScreenResolutionChanged(self):
        width, height = GUI.screenResolution()
        #BigWorld.logInfo(MOD_NAME, 'onScreenResolutionChanged: ({}, {})'.format(width, height), None)
        for panel in self.__panels:
            panel.updateScreenPosition(width, height)

    def onCrosshairViewChanged(self, viewID):
        #BigWorld.logInfo(MOD_NAME, 'crosshairViewChanged: {}'.format(CROSSHAIR_VIEW_SYMBOL[viewID]), None)
        self.changeView(viewID)

    def onCrosshairPositionChanged(self, x, y):
        #BigWorld.logInfo(MOD_NAME, 'onCrosshairPositionChanged: ({}, {})'.format(x, y), None)
        self.__crosshairPosition = [ x, y ]
        for panel in self.__panels:
            panel.updateCrosshairPosition(x, y)

    def onWatchStats(self):
        for panel in self.__panels:
            panel.update()

