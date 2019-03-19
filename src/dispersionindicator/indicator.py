
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
from test import IndicatorFlashText
from widget import PanelWidget, LabelWidget

import test


class Indicator(object):
    def __init__(self, config):
        self.__panels = {}
        self.__stats = g_dispersionStats
        updateInterval = config['default']['update_interval']
        self._timeInterval = TimeInterval(updateInterval, self, 'update')
        self.__populated = False

    def addPanel(self, name, config):
        return
        panel = IndicatorPanel(config, self.__stats)
        self.__panels[name] = panel

    def addLogger(self, config):
        logger = IndicatorLogger(config, self.__stats)
        self.__panels['__logger__'] = logger

    def addFlash(self, config):
        flash = IndicatorFlashText(config, self.__stats)
        self.__panels['__flash__'] = flash

    def onAvatarBecomePlayer(self):
        BigWorld.logInfo(MOD_NAME, 'onAvatarBecomePlayer', None)
        #avatar = BigWorld.player()
        #avatar.onVehicleEnterWorld += lambda _: self.populate()
        self.session = dependency.instance(IBattleSessionProvider)
        # VehicleStateController in gui.battle_control.controllers.vehicle_state_ctrl
        ctl = self.session.shared.vehicleState
        ctl.onVehicleControlling += self.onVehicleControlling
        #
        ctl = self.session.shared.crosshair
        ctl.onCrosshairPositionChanged += self.onCrosshairPositionChanged
        ctl.onCrosshairSizeChanged += lambda width, height: BigWorld.logInfo(MOD_NAME, 'crosshairSizeChanged: {}, {}'.format(width, height), None)
        ctl.onCrosshairViewChanged += lambda viewID: BigWorld.logInfo(MOD_NAME, 'crosshairViewChanged: {}'.format(viewID), None)
        g_guiResetters.add(self.onScreenResolutionChanged)
        for panel in self.__panels.values():
            panel.init()

    def onAvatarBecomeNonPlayer(self):
        BigWorld.logInfo(MOD_NAME, 'onAvatarBecomeNonPlayer', None)
        self.stop()
        g_guiResetters.discard(self.onScreenResolutionChanged)
        ctl = self.session.shared.crosshair
        if ctl:
            ctl.onVehicleStateUpdated -= self.onVehicleStateUpdated
            ctl.onVehicleControlling -= self.onVehicleControlling

    def onVehicleControlling(self, vehicle):
        BigWorld.logInfo(MOD_NAME, 'onVehicleControlling: {}'.format(vehicle), None)
        self.start()

    def onScreenResolutionChanged(self):
        for panel in self.__panels.values():
            if getattr(panel, 'updatePosition', None) and callable(panel.updatePosition):
                panel.updatePosition()

    def onCrosshairPositionChanged(self, x, y):
        for panel in self.__panels.values():
            if getattr(panel, 'updateCrosshairPosition', None) and callable(panel.updateCrosshairPosition):
                panel.updateCrosshairPosition(x, y)

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


class IndicatorPanel(object):
    def __init__(self, config, stats):
        self.stats = stats
        style = config['style']
        self.label_font = style['font']
        self.label_colour = tuple(style['colour'] + [ style['alpha'] ])
        self.line_height = style['line_height']
        self.padding_top = style['padding_top']
        self.padding_bottom = style['padding_bottom']
        self.padding_left = style['padding_left']
        self.padding_right = style['padding_right']
        self.panel_offset = style['panel_offset']
        self.panel_horizontalAnchor = str(style['horizontalAnchor'])
        self.panel_verticalAnchor = str(style['verticalAnchor'])
        self.stats_width = style['stats_width']
        self.bgimage = style['bgimage']
        self.statsdefs = config['stats_defs']
        self.panel = self.createWidgetTree(config['items'])
        self.panel.visible = False

    def init(self):
        self.panel.addRoot()
        self.updatePosition()

    def start(self):
        self.panel.visible = True
        
    def stop(self):
        self.panel.visible = False
        self.panel.delRoot()

    def update(self, *args):
        try:
            self.panel.update()
        except:
            BigWorld.logError(MOD_NAME, 'fail to update panel state', None)
    
    def enable(self):
        self.panel.visible = True
    
    def toggleVisible(self):
        self.panel.visible = not self.panel.visible

    def updatePosition(self):
        screen = GUI.screenResolution()
        center = ( screen[0] / 2, screen[1] / 2)
        x = center[0] + self.panel_offset[0]
        y = center[1] + self.panel_offset[1]
        self.panel.position = (x, y, 1)

    def createWidgetTree(self, items):
        panel = PanelWidget(self.bgimage)
        y = self.padding_top
        for name in items:
            setting = self.statsdefs[name]
            child = self.createPanelLine(setting)
            panel.addChild(child)
            child.position = (0, y, 1)
            y = y + child.height
        anchorx = max([ c.anchor[0] for c in panel.children ])
        for child in panel.children:
            pos = list(child.position)
            offsetx = anchorx - child.anchor[0]
            newpos = (pos[0] + offsetx + self.padding_left, pos[1], pos[2])
            child.position = newpos
        bx0 = min([ c.boundingBox[0] for c in panel.children])
        bx1 = max([ c.boundingBox[2] for c in panel.children])
        panel.width = bx1 - bx0 + self.padding_left + self.padding_right
        panel.height = y + self.padding_bottom
        panel.horizontalAnchor = self.panel_horizontalAnchor
        panel.verticalAnchor = self.panel_verticalAnchor
        return panel

    def createPanelLine(self, setting):
        name = setting['status']
        factor = setting['factor']
        template = setting['format']
        if isinstance(factor, str) or isinstance(factor, unicode):
            factor = CONSTANT.get(factor, 1.0)
        argList = {
            'title': {
                'text':     setting['title'],
                'align':    'RIGHT',
                'x':        - self.stats_width - 4
            },
            'stat': {
                'text':     template.format(0.0),
                'func':     lambda n=name, f=factor, t=template, s=self.stats: t.format(getattr(s, n, 0.0) * f),
                'align':    'RIGHT',
                'width':    self.stats_width,
                'x':        0
            },
            'unit': {
                'text':     setting['unit'],
                'x':        4
            }
        }
        panel = PanelWidget('')
        for name, kwargs in argList.items():
            label = self.createLabel(**kwargs)
            panel.addChild(label, name)
        bx0 = min([ c.boundingBox[0] for c in panel.children])
        bx1 = max([ c.boundingBox[2] for c in panel.children])
        for child in panel.children:
            pos = list(child.position)
            newpos = (pos[0] - bx0, pos[1], pos[2])
            child.position = newpos
        panel.anchor = [ - bx0, 0 ]
        panel.width = bx1 - bx0
        panel.height = self.line_height
        panel.visible = True
        panel.position = (0, 0, 1)
        return panel

    def createLabel(self, text='', func=None, align='LEFT', width=None, x=0):
        label = LabelWidget()
        label.text = text
        if func is not None:
            label.setCallback(func)
        label.font = self.label_font
        label.colour = self.label_colour
        label.horizontalAnchor = align
        label.position = (x, 0, 1)
        label.visible = True
        label.width = width
        return label
