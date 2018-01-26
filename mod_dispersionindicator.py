import math
import BigWorld
import GUI
from debug_utils import LOG_CURRENT_EXCEPTION
from gui import g_guiResetters
from gui.Scaleform.daapi.view.battle.shared.crosshair.plugins import ShotResultIndicatorPlugin
from Avatar import PlayerAvatar
from items.components import component_constants

MOD_NAME = 'DispersionIndicator'
LOG_FILE = 'mods/logs/chirimen.dispersionindicator/log.csv'

class Settings: pass

_strage = Settings()
_strage.info = {}

_strage.descr = (
    ('currTime',            'Current Time',     '{:.2f}',   1.0, '' ),
    ('vehicleSpeed',        'Vehicle Speed',    '{:.2f}',   1.0 / component_constants.KMH_TO_MS, 'km/s' ),
    ('vehicleRSpeed',       'Vehicle RSpeed',   '{:.2f}',   1.0, 'rad/s' ),
    ('turretRotationSpeed', 'Turret RSpeed',    '{:.2f}',   1.0, 'rad/s' ),
    ('additiveFactor',      'Additive Factor',  '{:.2f}',   1.0, '' ),
    ('dAngleAiming',        'DAngle Aiming',    '{:.2f}',   100.0, 'rad/100' ),
    ('dAngleIdeal',         'DAngle Ideal',     '{:.2f}',   100.0, 'rad/100' ),
    ('shotDispersionAngle', 'Shot DAngle',      '{:.2f}',   100.0, 'rad/100' ),
)

_strage.tags = [ 'currTime', '', 'turretRotationSpeed', ]

def outputLog():
    import os
    import csv
    
    try:
        os.makedirs(os.path.dirname(LOG_FILE))
    except:
        # LOG_CURRENT_EXCEPTION()
        pass
    with open(LOG_FILE, 'wb') as f:
        writer = csv.writer(f, dialect='excel')
        writer.writerows(_strage.data)


def playerAvatarAddon_getOwnVehicleShotDispersionAngle(self, *args, **kwargs):
    result = _strage.playerAvatar_getOwnVehicleShotDispersionAngle(self, *args, **kwargs)
    _strage.info['currTime'] = BigWorld.time()
    _strage.info['turretRotationSpeed'] = args[0]
    _strage.info['vehicleSpeed'], _strage.info['vehicleRSpeed'] = self.getOwnVehicleSpeeds(True)
    _strage.info['dAngleAiming'], _strage.info['dAngleIdeal'] = result
    descr = self._PlayerAvatar__getDetailedVehicleDescriptor()
    _strage.info['additiveFactor'] = self._PlayerAvatar__getAdditiveShotDispersionFactor(descr)
    _strage.info['shotDispersionAngle'] = descr.gun.shotDispersionAngle
    _strage.data.append([ _strage.info[tag[0]] for tag in _strage.descr ])
    return result


def shotResultIndicatorPluginAddon_start(self):
    result = _strage.ShotResultIndicatorPlugin_start(self)
    try:
        _strage.indicator = IndicatorPanel()
        _strage.indicator.start()
        _strage.data = []
        _strage.data.append([ tag[0] for tag in _strage.descr ])
    except:
        LOG_CURRENT_EXCEPTION()
    return result

def shotResultIndicatorPluginAddon_stop(self):
    result = _strage.ShotResultIndicatorPlugin_stop(self)
    try:
        if _strage.indicator:
            _strage.indicator.stop()
            _strage.indicator = None
        outputLog()
    except:
        LOG_CURRENT_EXCEPTION()
    return result

def shotResultIndicatorPluginAddon_onGunMarkerStateChanged(*args, **kwargs):
    result = _strage.ShotResultIndicatorPlugin_onGunMarkerStateChanged(*args, **kwargs)
    try:
        _strage.indicator.setInfo(_strage.info)
        _strage.indicator.setVisible(True)
    except:
        LOG_CURRENT_EXCEPTION()
    return result


def init():
    try:
        BigWorld.logInfo(MOD_NAME, '{} initialize'.format(MOD_NAME), None)
        _strage.playerAvatar_getOwnVehicleShotDispersionAngle = PlayerAvatar.getOwnVehicleShotDispersionAngle
        PlayerAvatar.getOwnVehicleShotDispersionAngle = playerAvatarAddon_getOwnVehicleShotDispersionAngle
        _strage.ShotResultIndicatorPlugin_start = ShotResultIndicatorPlugin.start
        ShotResultIndicatorPlugin.start = shotResultIndicatorPluginAddon_start
        _strage.ShotResultIndicatorPlugin_stop = ShotResultIndicatorPlugin.stop
        ShotResultIndicatorPlugin.stop = shotResultIndicatorPluginAddon_stop
        _strage.ShotResultIndicatorPlugin_onGunMarkerStateChanged = ShotResultIndicatorPlugin._ShotResultIndicatorPlugin__onGunMarkerStateChanged
        ShotResultIndicatorPlugin._ShotResultIndicatorPlugin__onGunMarkerStateChanged = shotResultIndicatorPluginAddon_onGunMarkerStateChanged
    except:
        LOG_CURRENT_EXCEPTION()


class IndicatorPanel(object):
    offset = (-170, 100)
    __active = False
    __tags = _strage.descr

    def __init__(self):
        self.window = GUI.Window('mods/chirimen.dispersionindicator/bgimage.dds')
        self.window.materialFX = 'BLEND'
        self.window.horizontalPositionMode = 'PIXEL'
        self.window.verticalPositionMode = 'PIXEL'
        self.window.widthMode = 'PIXEL'
        self.window.heightMode = 'PIXEL'
        self.window.width = 320
        self.window.height = 180
        self.window.visible = False
        self.labels = {}
        self.values = {}
        self.units = {}
        x = self.window.width
        y = 0
        y = y + 16
        for desc in self.__tags:
            name, text, form, factor, unit = desc
            self.labels[name] = self._genLabel(horizontalAnchor='RIGHT', text=text)
            self.values[name] = self._genLabel(horizontalAnchor='RIGHT')
            self.units[name] = self._genLabel(horizontalAnchor='LEFT', text=unit)
            self.labels[name].position = (x - 128, y, 1)
            self.values[name].position = (x - 64, y, 1)
            self.units[name].position = (x - 56, y, 1)
            self.window.addChild(self.labels[name])
            self.window.addChild(self.values[name])
            self.window.addChild(self.units[name])
            y = y + 16
 
    def _genLabel(self, **kwargs):
        label = GUI.Text('')
        label.font = 'default_small.font'
        label.horizontalAnchor = 'LEFT'
        label.verticalAnchor = 'TOP'
        label.horizontalPositionMode = 'PIXEL'
        label.verticalPositionMode = 'PIXEL'
        label.colour = (255, 255, 0, 180)
        label.colourFormatting = True
        label.visible = True
        for key, arg in kwargs.items():
            setattr(label, key, arg)
        return label
    
    def onScreenResolutionChanged(self):
        screen = GUI.screenResolution()
        center = ( screen[0] / 2, screen[1] / 2)
        right = center[0] + self.offset[0]
        top = center[1] + self.offset[1]
        self.window.horizontalAnchor = 'RIGHT'
        self.window.verticalAnchor = 'CENTER'
        self.window.position = (right, top, 1)

    def start(self):
        GUI.addRoot(self.window)
        self.onScreenResolutionChanged()
        g_guiResetters.add(self.onScreenResolutionChanged)
        self.__enable = True

    def stop(self):
        g_guiResetters.discard(self.onScreenResolutionChanged)
        GUI.delRoot(self.window)

    def setVisible(self, visible):
        self.__active = visible
        self.__applyVisible()

    def __applyVisible(self):
        if self.__active:
            self.window.visible = True
        else:
            self.window.visible = False

    def setInfo(self, info):
        if info:
            for desc in self.__tags:
                name, text, form, factor, unit = desc
                self.values[name].text = form.format(info[name] * factor)
        else:
            for desc in self._tags:
                name, text, form, factor, unit = desc
                self.values[name].text = ''


