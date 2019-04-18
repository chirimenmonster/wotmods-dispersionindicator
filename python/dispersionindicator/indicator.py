
import BigWorld
import GUI
from constants import ARENA_PERIOD
from gui import g_guiResetters
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.shared.utils.TimeInterval import TimeInterval
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, CROSSHAIR_VIEW_ID

from mod_constants import MOD_NAME, CONSTANT, CROSSHAIR_VIEW_SYMBOL, ARENA_PERIOD_SYMBOL
from status import g_dispersionStats
from output import IndicatorLogger
from flashPanel import IndicatorFlashText


class Indicator(object):
    def __init__(self, config):
        self.__panels = {}
        self.__stats = g_dispersionStats
        updateInterval = config['common']['updateInterval']
        self._timeInterval = TimeInterval(updateInterval, self, 'update')
        self.__isSetHandler = False
        self.__populated = False
        for name, paneldef in config['panels'].items():
            self.__panels[name] = IndicatorFlashText(paneldef, self.__stats, name)
        if 'logs' in config:
            self.__panels['__logger__'] = IndicatorLogger(config['logs'], self.__stats)

    def initPanel(self):
        BigWorld.logInfo(MOD_NAME, 'initPanel', None)
        arena = BigWorld.player().arena
        arena.onPeriodChange += self.onArenaPeriodChange
        self.addHandler()
        for name, panel in self.__panels.items():
            panel.init()

    def finiPanel(self):
        BigWorld.logInfo(MOD_NAME, 'finiPanel', None)
        self.stopIntervalTimer()
        self.invisiblePanel()
        self.removeHandler()

    def onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        BigWorld.logInfo(MOD_NAME, 'onArenaPeriodChange: {}'.format(ARENA_PERIOD_SYMBOL[period]), None)
        if period == ARENA_PERIOD.PREBATTLE:
            self.visiblePanel()
        elif period == ARENA_PERIOD.BATTLE:
            self.startIntervalTimer()
        elif period == ARENA_PERIOD.AFTERBATTLE:
            self.invisiblePanel()

    def onVehicleStateUpdated(self, stateID, value):
        if stateID == VEHICLE_VIEW_STATE.DESTROYED:
            BigWorld.logInfo(MOD_NAME, 'onVehicleStateUpdated: VEHICLE_VIEW_STATE.DESTROYED', None)
            self.finiPanel()
    
    def onScreenResolutionChanged(self):
        for panel in self.__panels.values():
            if getattr(panel, 'updateScreenPosition', None) and callable(panel.updateScreenPosition):
                panel.updateScreenPosition()

    def onCrosshairViewChanged(self, viewID):
        #BigWorld.logInfo(MOD_NAME, 'crosshairViewChanged: {}'.format(CROSSHAIR_VIEW_SYMBOL[viewID]), None)
        self.changeView(viewID)

    def onCrosshairPositionChanged(self, x, y):
        for panel in self.__panels.values():
            if getattr(panel, 'updateCrosshairPosition', None) and callable(panel.updateCrosshairPosition):
                panel.updateCrosshairPosition(x, y)

    def addHandler(self):
        if self.__isSetHandler:
            return
        self.__isSetHandler = True
        session = dependency.instance(IBattleSessionProvider)
        # VehicleStateController in gui.battle_control.controllers.vehicle_state_ctrl
        ctl = session.shared.vehicleState
        ctl.onVehicleStateUpdated += self.onVehicleStateUpdated
        # CrosshairDataProxy in gui.battle_control.controllers.crosshair_proxy
        ctl = session.shared.crosshair
        ctl.onCrosshairViewChanged += self.onCrosshairViewChanged
        ctl.onCrosshairPositionChanged += self.onCrosshairPositionChanged
        #ctl.onCrosshairSizeChanged += lambda width, height: BigWorld.logInfo(MOD_NAME, 'crosshairSizeChanged: {}, {}'.format(width, height), None)
        g_guiResetters.add(self.onScreenResolutionChanged)
        self.changeView(ctl.getViewID())
    
    def removeHandler(self):
        if not self.__isSetHandler:
            return
        self.__isSetHandler = False
        g_guiResetters.remove(self.onScreenResolutionChanged)
        session = dependency.instance(IBattleSessionProvider)
        # VehicleStateController in gui.battle_control.controllers.vehicle_state_ctrl
        ctl = session.shared.vehicleState
        if ctl:
            ctl.onVehicleStateUpdated -= self.onVehicleStateUpdated
        # CrosshairDataProxy in gui.battle_control.controllers.crosshair_proxy
        ctl = session.shared.crosshair
        if ctl:
            ctl.onCrosshairViewChanged -= self.onCrosshairViewChanged
            ctl.onCrosshairPositionChanged -= self.onCrosshairPositionChanged

    def visiblePanel(self):
        if self.__populated:
            return
        self.__populated = True
        BigWorld.logInfo(MOD_NAME, 'panel.start', None)
        for panel in self.__panels.values():
            panel.start()

    def invisiblePanel(self):
        if not self.__populated:
            return
        self.__populated = False
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
        
    def update(self):
        for panel in self.__panels.values():
            panel.update()

    def changeView(self, viewID):
        #BigWorld.logInfo(MOD_NAME, 'changeView: {}'.format(CROSSHAIR_VIEW_SYMBOL[viewID]), None)
        for panel in self.__panels.values():
            if getattr(panel, 'changeView', None) and callable(panel.changeView):
                panel.changeView(viewID)
