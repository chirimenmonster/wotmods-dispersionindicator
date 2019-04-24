
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
from status import g_dispersionStats
from statsindicator import StatsIndicator
from statslogger import StatsLogger


class IndicatorManager(object):
    def __init__(self, config):
        self.__config = config
        self.__panels = {}
        self.__stats = g_dispersionStats
        self.__isSetHandler = False
        self.__visible = False
        interval = config['common']['updateInterval']
        self._timeInterval = TimeInterval(interval, self, 'onWatchStats')
        g_eventBus.addListener(events.AppLifeCycleEvent.INITIALIZED, self.onAppInitialized)
        g_eventBus.addListener(events.AppLifeCycleEvent.DESTROYED, self.onAppDestroyed)
        # Embedded file name: scripts/client/gui/app_loader/loader.py
        g_appLoader.onGUISpaceEntered += self.onGUISpaceEntered
        g_appLoader.onGUISpaceLeft += self.onGUISpaceLeft

    def initPanel(self):
        BigWorld.logInfo(MOD_NAME, 'initPanel', None)
        arena = BigWorld.player().arena
        arena.onPeriodChange += self.onArenaPeriodChange
        self.addHandler()
        for name, paneldef in self.__config['panels'].items():
            self.__panels[name] = StatsIndicator(paneldef, self.__stats, name)
        if 'logs' in self.__config:
            self.__panels['__logger__'] = IndicatorLogger(self.__config['logs'], self.__stats)
        for name, panel in self.__panels.items():
            panel.init()
        self.updateScreenPosition()

    def finiPanel(self):
        BigWorld.logInfo(MOD_NAME, 'finiPanel', None)
        self.stopIntervalTimer()
        self.invisiblePanel()
        self.removeHandler()
        self._panels = {}

    def addHandler(self):
        if self.__isSetHandler:
            return
        self.__isSetHandler = True
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
        for panel in self.__panels.values():
            panel.start()

    def invisiblePanel(self):
        if not self.__visible:
            return
        self.__visible = False
        BigWorld.logInfo(MOD_NAME, 'panel.stop', None)
        for panel in self.__panels.values():
            panel.stop()

    def startIntervalTimer(self):
        if not self._timeInterval.isStarted():
            BigWorld.logInfo(MOD_NAME, 'TimeInterval: start', None)
            self._timeInterval.start()

    def stopIntervalTimer(self):
        if self._timeInterval.isStarted():
            BigWorld.logInfo(MOD_NAME, 'TimeInterval: stop', None)
            self._timeInterval.stop()

    def changeView(self, viewID):
        #BigWorld.logInfo(MOD_NAME, 'changeView: {}'.format(CROSSHAIR_VIEW_SYMBOL[viewID]), None)
        for panel in self.__panels.values():
            if getattr(panel, 'changeView', None) and callable(panel.changeView):
                panel.changeView(viewID)

    def updateScreenPosition(self):
        width, height = GUI.screenResolution()
        BigWorld.logInfo(MOD_NAME, 'updateScreenPosition: ({}, {})'.format(width, height), None)
        for panel in self.__panels.values():
            if getattr(panel, 'updateScreenPosition', None) and callable(panel.updateScreenPosition):
                panel.updateScreenPosition(width, height)

    def onAppInitialized(self, event):
        if event.ns != APP_NAME_SPACE.SF_BATTLE:
            return
        BigWorld.logInfo(MOD_NAME, 'AppLifeCycleEvent.INITIALIZED: SF_BATTLE', None)
        self.initPanel()

    def onAppDestroyed(self, event):
        if event.ns != APP_NAME_SPACE.SF_BATTLE:
            return
        BigWorld.logInfo(MOD_NAME, 'AppLifeCycleEvent.DESTROYED: SF_BATTLE', None)
        self.finiPanel()

    def onGUISpaceEntered(self, spaceID):
        if spaceID != GUI_GLOBAL_SPACE_ID.BATTLE:
            return
        BigWorld.logInfo(MOD_NAME, 'onGUISpaceEnterd: {}'.format(spaceID), None)
        #self.initPanel()
    
    def onGUISpaceLeft(self, spaceID):
        if spaceID != GUI_GLOBAL_SPACE_ID.BATTLE:
            return
        BigWorld.logInfo(MOD_NAME, 'onGUISpaceLeft: {}'.format(spaceID), None)

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
        BigWorld.logInfo(MOD_NAME, 'onScreenResolutionChanged: ({}, {})'.format(width, height), None)
        for panel in self.__panels.values():
            if getattr(panel, 'updateScreenPosition', None) and callable(panel.updateScreenPosition):
                panel.updateScreenPosition(width, height)

    def onCrosshairViewChanged(self, viewID):
        #BigWorld.logInfo(MOD_NAME, 'crosshairViewChanged: {}'.format(CROSSHAIR_VIEW_SYMBOL[viewID]), None)
        self.changeView(viewID)

    def onCrosshairPositionChanged(self, x, y):
        BigWorld.logInfo(MOD_NAME, 'onCrosshairPositionChanged: ({}, {})'.format(x, y), None)
        for panel in self.__panels.values():
            if getattr(panel, 'updateCrosshairPosition', None) and callable(panel.updateCrosshairPosition):
                panel.updateCrosshairPosition(x, y)

    def onWatchStats(self):
        for panel in self.__panels.values():
            panel.update()

