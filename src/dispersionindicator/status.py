
import math
import BigWorld
from gui import g_guiResetters

from panel import Panel


BGIMAGE_FILE = '${resource_dir}/bgimage.dds'
DEFAULT_WIDTH = 280
DEFAULT_HEIGHT = 16

CONSTANT = {
    'MS_TO_KMH':    3600.0 / 1000.0
}

class Config:
    colour = (255, 255, 0)
    alpha = 127
    font = 'default_small.font'
    padding_top = 4
    padding_bottom = 4
    panel_width = 280
    panel_offset = (-200, 50)
    line_height = 16
    bgimage = BGIMAGE_FILE

g_config = Config()


def init():
    global g_status
    global g_panel
    g_status = Status()
    g_panel = IndicatorPanel()

def shotResultIndicatorPlugin_start(orig, self, *args, **kwargs):
    result = orig(self, *args, **kwargs)
    g_panel.start()
    return result

def shotResultIndicatorPlugin_stop(orig, self, *args, **kwargs):
    g_panel.stop()
    result = orig(self, *args, **kwargs)
    return result

def shotResultIndicatorPlugin_onGunMarkerStateChanged(orig, self, *args, **kwargs):
    result = orig(self, *args, **kwargs)
    g_panel.update()
    return result

def playerAvatar_getOwnVehicleShotDispersionAngle(orig, self, turretRotationSpeed, withShot = 0):
    result = orig(self, turretRotationSpeed, withShot)
    avatar = self
    g_status.dAngleAiming = result[0]
    g_status.dAngleIdeal = result[1]
    g_status.turretRotationSpeed = turretRotationSpeed
    g_status.withShot = withShot
    g_status._getOwnVehicleShotDispersionAngle(avatar)
    return result


class IndicatorPanel(object):
    def __init__(self):
        self.label_font = g_config.font
        self.label_colour = g_config.colour + (g_config.alpha, )
        self.line_height = g_config.line_height
        self.padding_top = g_config.padding_top
        self.padding_bottom = g_config.padding_bottom
        self.panel_offset = g_config.panel_offset
        self.panel_width = g_config.panel_width
        self.bgimage = g_config.bgimage
        self.panel = createWidgetTree()

    def start(self):
        print 'panel.start'
        self.panel.addRoot()
        g_guiResetters.add(self.onScreenResolutionChanged)
        self.updatePosition()
        self.panel.visible = True
        
    def stop(self):
        print 'panel.stop'
        g_guiResetters.discard(self.onScreenResolutionChanged)
        self.panel.visible = False
        self.panel.delRoot()

    def toggleVisible(self):
        self.panel.visible = not self.panel.visible

    def onGunMarkerStateChanged(self):
        self.panel.update()

    def onScreenResolutionChanged(self):
        self.updatePosition()

    def updatePosition(self):
        screen = GUI.screenResolution()
        center = ( screen[0] / 2, screen[1] / 2)
        x = center[0] + self.panel_offset[0]
        y = center[1] + self.panel_offset[1]
        self.panel.position = (x, y, 1)
        print self.panel.position, self.panel.width, self.panel.height

    def createWidgetTree(self):
        panel = PanelWidget(self.bgimage)
        y = self.padding_top
        for setting in g_config['panelItems']:
            child = self.createPanelLine(setting)
            panel.addChild(child)
            child.position = (0, y, 1)
            y = y + child.height
        panel.width = self.panel_width
        panel.height = y + self.padding_bottom
        panel.horizontalAnchor = 'RIGHT'
        panel.verticalAnchor = 'CENTER'
        return panel

    def createPanelLine(self, setting):
        name = setting['status']
        factor = setting['factor']
        template = setting['format']
        if isinstance(factor, str):
            factor = CONSTANT.get(factor, 1.0)
        argList = [
            {
                'text':     setting['title'],
                'align':    'RIGHT',
                'x':        width - 128
            },
            {
                'func':     lambda n=name, f=factor, t=template: t.format(getattr(g_status, n) * f),
                'align':    'RIGHT',
                'x':        width - 72    
            },
            {
                'text':     setting['unit'],
                'x':        width - 60
            }
        ]
        panel = PanelWidget(self.bgimage)
        for kwarg in argList:
            label = LabelWidget(**kwarg)
            panel.addChild(label)
        panel.width = self.panel_width
        panel.height = self.line_height
        panel.visible = True
        return panel

    def createLabel(self, text=None, func=None, align='LEFT', x=0):
        label = LabelWidget()
        if text is not None:
            label.text = text
        if func is not None:
            label.setCallback(func)
        label.font = self.label_font
        label.colour = self.label_colour
        label.horizontalAnchor = align
        label.position = (x, 0, 1)
        label.visible = True
        return label


class Status(object):
    def _getOwnVehicleShotDispersionAngle(self, avatar):
        self.currTime = BigWorld.time()
        vDescr = avatar._PlayerAvatar__getDetailedVehicleDescriptor()
        self.additiveFactor = avatar._PlayerAvatar__getAdditiveShotDispersionFactor(vDescr)
        self.shotDispersionAngle = vDescr.gun.shotDispersionAngle
        if self.withShot == 0:
            self.shotFactor = 0.0
        elif self.withShot == 1:
            self.shotFactor = vDescr.gun.shotDispersionFactors['afterShot']
        else:
            self.shotFactor = vDescr.gun.shotDispersionFactors['afterShotInBurst']
        self._update_aimingInfo(avatar)
        self._update_vehicleSpeeds(avatar)
        self._update_vehicleEngineState(avatar)

    def _update_aimingInfo(self, avatar):
        aimingInfo = avatar._PlayerAvatar__aimingInfo
        self.aimingStartTime = aimingInfo[0]
        self.aimingStartFactor = aimingInfo[1]
        self.multFactor = aimingInfo[2]
        self.factorsTurretRotation = aimingInfo[3]
        self.factorsMovement = aimingInfo[4]
        self.factorsRotation = aimingInfo[5]
        self.aimingTime = aimingInfo[6]

    def _update_vehicleSpeeds(self, avatar):
        vehicleSpeed, vehicleRSpeed = avatar.getOwnVehicleSpeeds(True)
        self.vehicleSpeed = vehicleSpeed
        self.vehicleRSpeed = vehicleRSpeed

    def _update_vehicleEngineState(self, avatar):
        detailedEngineState = avatar.vehicle.appearance._CompoundAppearance__detailedEngineState
        self.engineRPM = detailedEngineState.rpm
        self.engineRelativeRPM = detailedEngineState.relativeRPM

    @property
    def aimingFactor(self):
        return self.dAngleAiming / self.shotDispersionAngle

    @property
    def aimingTimeConverging(self):
        return self.aimingStartTime + self.aimingTime * math.log(self.aimingStartFactor) - self.currTime

    @property
    def scoreDispersion(self):
        return (math.log(self.aimingFactor) / math.log(4.0)) ** 2 * 100.0
