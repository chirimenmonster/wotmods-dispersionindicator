
import logging
import BigWorld
from gui.Scaleform.framework import ViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.framework.entities.View import View

MOD_NAME = '${name}'

PANEL_VIEW_ALIAS = 'DispersionIndicatorPanel'
PANEL_VIEW_SWF_FILE_PATH = 'dispersionindicator/IndicatorPanel.swf'

for name in [ 'gui.Scalform.framework.entities.View', 'gui.Scaleform.Flash' ]:
    logging.getLogger(name).setLevel(logging.DEBUG)
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class PanelView(View):
    def setConfig(self, config, style):
        self.__config = config
        self.__style = style

    def getConfig(self):
        BigWorld.logInfo(MOD_NAME, 'getConfig', None)
        self.flashObject.as_setConfig(self.__config, self.__style)

    def as_setPositionS(self, x, y):
        BigWorld.logInfo(MOD_NAME, 'as_setPositionS: ({}, {})'.format(x, y), None)
        self.flashObject.as_setPosition(x, y)

    def as_setValueS(self, name, value):
        BigWorld.logInfo(MOD_NAME, 'as_setValueS: ({}, {})'.format(name, value), None)
        self.flashObject.as_setValue(name, value)

    def getPanelSize(self):
        BigWorld.logInfo(MOD_NAME, 'getPanelSize', None)
        width = int(self.flashObject.fieldWidth)
        height = int(self.flashObject.fieldHeight)
        return width, height


PANEL_VIEW_SETTINGS = ViewSettings(
    PANEL_VIEW_ALIAS,
    PanelView,
    PANEL_VIEW_SWF_FILE_PATH,
    ViewTypes.WINDOW,
    None,
    ScopeTemplates.DEFAULT_SCOPE
)
