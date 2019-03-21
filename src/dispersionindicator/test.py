
import BigWorld
import GUI
from gui.Scaleform.Flash import Flash

from constants import MOD_NAME, CONSTANT


class IndicatorFlashText(object):
    def __init__(self, config, stats):
        self.stats = stats
        style = config['style']
        #self.panel_offset = style['panel_offset']
        self.panel_offset = [ 140, -8 ]
        flash = Flash('TestProject.swf', path='gui/scaleform')
        flash.movie.backgroundAlpha = 0.0
        flash.movie.scaleMode = 'NoScale'
        flash.component.heightMode = 'PIXEL'
        flash.component.widthMode = 'PIXEL'
        flash.component.wg_inputKeyMode = 2
        flash.component.focus = False
        flash.component.moveFocus = False
        flash.movie.root.as_createPanel([
            { "label": "time", "unit": "s" },
            { "label": "angle", "unit": "rad/100" },
            { "label": "velocity", "unit": "km/h" }
        ])
        self.flash = flash
 

    def init(self):
        BigWorld.logInfo(MOD_NAME, 'flashText.init', None)
        self.updatePosition()

    def start(self):
        BigWorld.logInfo(MOD_NAME, 'flashText.start', None)
        self.flash.active(True)

    def stop(self):
        BigWorld.logInfo(MOD_NAME, 'frashText.stop', None)
        self.flash.active(False)
   
    def update(self):
        data = getattr(self.stats, 'aimingTimeConverging', 0.0)
        #BigWorld.logInfo(MOD_NAME, 'frashText.update', None)
        self.flash.movie.root.as_setText('{:.2f}'.format(data))

    def updatePosition(self):
        screen = GUI.screenResolution()
        center = ( screen[0] / 2, screen[1] / 2)
        x = center[0] + self.panel_offset[0]
        y = center[1] + self.panel_offset[1]
        BigWorld.logInfo(MOD_NAME, 'frashText.updatePosition ({}, {})'.format(x, y), None)
        self.flash.movie.root.as_setPosition(int(x), int(y))

    def updateCrosshairPosition(self, x, y):
        x = x + self.panel_offset[0]
        y = y + self.panel_offset[1]
        BigWorld.logInfo(MOD_NAME, 'frashText.updateCrosshairPosition ({}, {})'.format(x, y), None)
        self.flash.movie.root.as_setPosition(int(x), int(y))
