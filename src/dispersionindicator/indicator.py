
import BigWorld
import GUI
from gui import g_guiResetters
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.shared.utils.TimeInterval import TimeInterval
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE

from constants import MOD_NAME, CONSTANT
from status import g_dispersionStats
from output import IndicatorLogger
from flashPanel import IndicatorFlashText


class Indicator(object):
    def __init__(self, config):
        self.__panels = {}
        self.__stats = g_dispersionStats
        updateInterval = config['default']['update_interval']
        self._timeInterval = TimeInterval(updateInterval, self, 'update')
        self.__isSetHandler = False
        self.__populated = False

    def addFlashPanel(self, name, config):
        flash = IndicatorFlashText(config, self.__stats)
        self.__panels[name] = flash

    def addLogger(self, config):
        logger = IndicatorLogger(config, self.__stats)
        self.__panels['__logger__'] = logger


    def onAvatarBecomePlayer(self):
        BigWorld.logInfo(MOD_NAME, 'onAvatarBecomePlayer', None)
        self.addHandler()
        for panel in self.__panels.values():
            panel.init()

    def onAvatarBecomeNonPlayer(self):
        BigWorld.logInfo(MOD_NAME, 'onAvatarBecomeNonPlayer', None)
        self.stop()
        self.removeHandler()

    def onVehicleControlling(self, vehicle):
        BigWorld.logInfo(MOD_NAME, 'onVehicleControlling: {}'.format(vehicle), None)
        self.start()

    def onVehicleStateUpdated(self, stateID, value):
        if stateID == VEHICLE_VIEW_STATE.DESTROYED:
            BigWorld.logInfo(MOD_NAME, 'onVehicleStateUpdated: VEHICLE_VIEW_STATE.DESTROYED', None)
            self.stop()
            self.removeHandler()
    
    def onScreenResolutionChanged(self):
        for panel in self.__panels.values():
            if getattr(panel, 'updateScreenPosition', None) and callable(panel.updateScreenPosition):
                panel.updateScreenPosition()

    def onCrosshairPositionChanged(self, x, y):
        for panel in self.__panels.values():
            if getattr(panel, 'updateCrosshairPosition', None) and callable(panel.updateCrosshairPosition):
                panel.updateCrosshairPosition(x, y)

    def addHandler(self):
        if self.__isSetHandler:
            return
        self.__isSetHandler = True
        self.session = dependency.instance(IBattleSessionProvider)
        # VehicleStateController in gui.battle_control.controllers.vehicle_state_ctrl
        ctl = self.session.shared.vehicleState
        ctl.onVehicleControlling += self.onVehicleControlling
        ctl.onVehicleStateUpdated += self.onVehicleStateUpdated
        # CrosshairDataProxy in gui.battle_control.controllers.crosshair_proxy
        ctl = self.session.shared.crosshair
        ctl.onCrosshairPositionChanged += self.onCrosshairPositionChanged
        ctl.onCrosshairSizeChanged += lambda width, height: BigWorld.logInfo(MOD_NAME, 'crosshairSizeChanged: {}, {}'.format(width, height), None)
        ctl.onCrosshairViewChanged += lambda viewID: BigWorld.logInfo(MOD_NAME, 'crosshairViewChanged: {}'.format(viewID), None)
        g_guiResetters.add(self.onScreenResolutionChanged)
    
    def removeHandler(self):
        if not self.__isSetHandler:
            return
        self.__isSetHandler = False
        g_guiResetters.remove(self.onScreenResolutionChanged)
        self.session = dependency.instance(IBattleSessionProvider)
        # VehicleStateController in gui.battle_control.controllers.vehicle_state_ctrl
        ctl = self.session.shared.vehicleState
        ctl.onVehicleControlling -= self.onVehicleControlling
        ctl.onVehicleStateUpdated -= self.onVehicleStateUpdated
        # CrosshairDataProxy in gui.battle_control.controllers.crosshair_proxy
        ctl = self.session.shared.crosshair
        ctl.onCrosshairPositionChanged -= self.onCrosshairPositionChanged
        ctl.onCrosshairSizeChanged -= lambda width, height: BigWorld.logInfo(MOD_NAME, 'crosshairSizeChanged: {}, {}'.format(width, height), None)
        ctl.onCrosshairViewChanged -= lambda viewID: BigWorld.logInfo(MOD_NAME, 'crosshairViewChanged: {}'.format(viewID), None)

    def start(self):
        if self.__populated:
            return
        self.__populated = True
        BigWorld.logInfo(MOD_NAME, 'panel.start', None)
        for panel in self.__panels.values():
            panel.start()
        if not self._timeInterval.isStarted():
            BigWorld.logInfo(MOD_NAME, 'TimeInterval: start', None)
            self._timeInterval.start()

    def stop(self):
        if not self.__populated:
            return
        self.__populated = False
        BigWorld.logInfo(MOD_NAME, 'panel.stop', None)
        if self._timeInterval.isStarted():
            BigWorld.logInfo(MOD_NAME, 'TimeInterval: stop', None)
            self._timeInterval.stop()
        for panel in self.__panels.values():
            panel.stop()
        
    def update(self):
        for panel in self.__panels.values():
            panel.update()
