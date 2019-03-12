
import math
import json
import BigWorld
import ResMgr
import GUI
from debug_utils import LOG_CURRENT_EXCEPTION
from gui import g_guiResetters
from gui.Scaleform.daapi.view.battle.shared.crosshair.plugins import ShotResultIndicatorPlugin
from Avatar import PlayerAvatar
from items.components import component_constants

from dispersionindicator.events import overrideMethod
from dispersionindicator import panel
from dispersionindicator import status

MOD_NAME = '${name}'
LOG_FILE = '${logfile}'
BGIMAGE_FILE = '${resource_dir}/bgimage.dds'
DEFAULT_CONFIG_FILE = '${resource_dir}/config.json'
CONFIG_FILE = '${config_file}'


class Strage:
    info = {}
    indicator = None

_strage = Strage()
_strage.descr = [
    ('currTime',            'Current Time',     '{:.2f}',   1.0, 's' ),
    ('vehicleSpeed',        'Vehicle Speed',    '{:.2f}',   1.0 / component_constants.KMH_TO_MS, 'km/h' ),
    ('vehicleRSpeed',       'Vehicle RSpeed',   '{:.2f}',   1.0, 'rad/s' ),
    ('speedInfo0',          'speedInfo[0]',     '{:.2f}',   1.0 / component_constants.KMH_TO_MS, 'km/h' ),
    ('engineRPM',           'Engine RPM',       '{:.0f}',   1.0,    'rpm'   ),
    ('engineRelativeRPM',   'Engine Relative RPM',  '{:.2f}',   1.0,    'rpm'   ),
    ('turretRotationSpeed', 'Turret RSpeed',    '{:.2f}',   1.0, 'rad/s' ),
    ('additiveFactor',      'Additive Factor',  '{:.2f}',   1.0, '' ),
    ('dAngleAiming',        'Aiming DAngle',    '{:.2f}',   100.0, 'rad/100' ),
    ('dAngleIdeal',         'Ideal DAngle',     '{:.2f}',   100.0, 'rad/100' ),
    ('shotDispersionAngle', 'Shot DAngle',      '{:.2f}',   100.0, 'rad/100' ),
    ('aimingStartTime',     'Aiming Start Time',    '{:.2f}',   1.0, 's'),
    ('aimingStartFactor',   'Aiming Start Factor',  '{:.2f}',   1.0, ''),
    ('aimingTime',          'Aiming Time',      '{:.2f}',   1.0, 's'),
    ('multFactor',          'Mult. Factor',     '{:.2f}',   1.0, ''),
    ('factorsMovement',     'Movement Factor',  '{:.2f}',   1.0, ''),
    ('factorsRotation',     'Rotation Factor',  '{:.2f}',   1.0, ''),
    ('factorsTurretRotation',   'TurretR Factor',   '{:.2f}', 1.0, ''),
    ('shotFactor',          'Shot Factor',      '{:.2f}',   1.0, ''),
]


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


@overrideMethod(PlayerAvatar, 'getOwnVehicleShotDispersionAngle')
def playerAvatarAddon_getOwnVehicleShotDispersionAngle(orig, self, turretRotationSpeed, withShot = 0):
    return status.playerAvatar_getOwnVehicleShotDispersionAngle(orig, self, turretRotationSpeed, withShot = 0)

    result = orig(self, turretRotationSpeed, withShot)
    _strage.info['currTime'] = BigWorld.time()
    _strage.info['turretRotationSpeed'] = turretRotationSpeed
    _strage.info['vehicleSpeed'], _strage.info['vehicleRSpeed'] = self.getOwnVehicleSpeeds(True)
    
    _strage.info['speedInfo0'] = self.vehicle.getSpeed()
    _strage.info['engineRPM'] = self.vehicle.appearance._CompoundAppearance__detailedEngineState.rpm
    _strage.info['engineRelativeRPM'] = self.vehicle.appearance._CompoundAppearance__detailedEngineState.relativeRPM

    _strage.info['dAngleAiming'], _strage.info['dAngleIdeal'] = result
    descr = self._PlayerAvatar__getDetailedVehicleDescriptor()
    _strage.info['additiveFactor'] = self._PlayerAvatar__getAdditiveShotDispersionFactor(descr)
    _strage.info['shotDispersionAngle'] = descr.gun.shotDispersionAngle
    aimingStartTime, aimingStartFactor, multFactor, gunShotDispersionFactorsTurretRotation, chassisShotDispersionFactorsMovement, chassisShotDispersionFactorsRotation, aimingTime = self._PlayerAvatar__aimingInfo
    _strage.info['aimingStartTime'] = aimingStartTime
    _strage.info['aimingStartFactor'] = aimingStartFactor
    _strage.info['multFactor'] = multFactor
    _strage.info['factorsTurretRotation'] = gunShotDispersionFactorsTurretRotation
    _strage.info['factorsMovement'] = chassisShotDispersionFactorsMovement
    _strage.info['factorsRotation'] = chassisShotDispersionFactorsRotation
    _strage.info['aimingTime'] = aimingTime
    if withShot == 0:
        _strage.info['shotFactor'] = 0
    elif withShot == 1:
        _strage.info['shotFactor'] = descr.gun.shotDispersionFactors['afterShot']
    else:
        _strage.info['shotFactor'] = descr.gun.shotDispersionFactors['afterShotInBurst']
    _strage.data.append([ _strage.info.get(tag[0], None) for tag in _strage.descr ])
    return result


@overrideMethod(ShotResultIndicatorPlugin, 'start')
def shotResultIndicatorPluginAddon_start(orig, self, *args, **kwargs):
    return status.shotResultIndicatorPlugin_start(orig, self, *args, **kwargs)
    result = orig(self, *args, **kwargs)
    try:
        _strage.indicator = IndicatorPanel()
        _strage.indicator.start()
        _strage.data = []
        _strage.data.append([ tag[0] for tag in _strage.descr ])
    except:
        LOG_CURRENT_EXCEPTION()
    return result

@overrideMethod(ShotResultIndicatorPlugin, 'stop')
def shotResultIndicatorPluginAddon_stop(orig, self, *args, **kwargs):
    return status.shotResultIndicatorPlugin_stop(orig, self, *args, **kwargs)
    result = orig(self, *args, **kwargs)
    try:
        if _strage.indicator:
            _strage.indicator.stop()
            _strage.indicator = None
        outputLog()
    except:
        LOG_CURRENT_EXCEPTION()
    return result

@overrideMethod(ShotResultIndicatorPlugin, '_ShotResultIndicatorPlugin__onGunMarkerStateChanged')
def shotResultIndicatorPluginAddon_onGunMarkerStateChanged(orig, self, *args, **kwargs):
    return status.shotResultIndicatorPlugin_onGunMarkerStateChanged(orig, self, *args, **kwargs)
    result = orig(self, *args, **kwargs)
    try:
        _strage.indicator.setInfo(_strage.info)
        _strage.indicator.setVisible(True)
    except:
        LOG_CURRENT_EXCEPTION()
    return result


def init():
    try:
        BigWorld.logInfo(MOD_NAME, '{} initialize'.format(MOD_NAME), None)
        if not ResMgr.isFile(DEFAULT_CONFIG_FILE):
            BigWorld.logInfo(MOD_NAME, 'file is not found: {}'.format(DEFAULT_CONFIG_FILE), None)
            raise
        file = ResMgr.openSection(DEFAULT_CONFIG_FILE)
        config = json.loads(file.asString)
        print json.dumps(config, indent=2)
        if ResMgr.isFile(CONFIG_FILE):
            BigWorld.logInfo(MOD_NAME, 'found config: {}'.format(CONFIG_FILE), None)
            file = ResMgr.openSection(CONFIG_FILE)
            config = json.loads(file.asString)
            print json.dumps(config, indent=2)
            BigWorld.logInfo(MOD_NAME, 'load config: {}'.format(CONFIG_FILE), None)
        status.g_config.config = config
        status.init()
    except:
        LOG_CURRENT_EXCEPTION()


class IndicatorPanel(object):
    offset = (-200, 50)
    __active = False
    __tags = _strage.descr

    def __init__(self):
        self.window = GUI.Window(BGIMAGE_FILE)
        self.window.materialFX = 'BLEND'
        self.window.horizontalPositionMode = 'PIXEL'
        self.window.verticalPositionMode = 'PIXEL'
        self.window.widthMode = 'PIXEL'
        self.window.heightMode = 'PIXEL'
        self.window.width = 280
        self.window.visible = False
        self.labels = {}
        self.values = {}
        self.units = {}
        x = self.window.width
        y = 0
        y = y + 8
        for desc in self.__tags:
            name, text, form, factor, unit = desc
            self.labels[name] = self._genLabel(horizontalAnchor='RIGHT', text=text)
            self.values[name] = self._genLabel(horizontalAnchor='RIGHT')
            self.units[name] = self._genLabel(horizontalAnchor='LEFT', text=unit)
            self.labels[name].position = (x - 128, y, 1)
            self.values[name].position = (x - 72, y, 1)
            self.units[name].position = (x - 60, y, 1)
            self.window.addChild(self.labels[name])
            self.window.addChild(self.values[name])
            self.window.addChild(self.units[name])
            y = y + 16
        self.window.height = y + 8
 
    def _genLabel(self, **kwargs):
        label = GUI.Text('')
        label.font = 'default_small.font'
        label.horizontalAnchor = 'LEFT'
        label.verticalAnchor = 'TOP'
        label.horizontalPositionMode = 'PIXEL'
        label.verticalPositionMode = 'PIXEL'
        label.colour = (255, 255, 0, 127)
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
        for desc in self.__tags:
            name, text, form, factor, unit = desc
            value = info.get(name, None) if info is not None else None
            self.values[name].text = form.format(info[name] * factor) if value is not None else ''


