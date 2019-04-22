
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
    def __init__(self, *args, **kwargs):
        super(PanelView, self).__init__(*args, **kwargs)
        self.onCreated += self.__onCreated

    def __onCreated(self, pyView):
        BigWorld.logInfo(MOD_NAME, 'PanelView: onCreated', None)
        self.flashObject.visible = False

    def as_setConfigS(self, settings):
        BigWorld.logInfo(MOD_NAME, 'PanelView: as_setConfigS', None)
        self.flashObject.as_setConfig(settings)

    def as_setPositionS(self, x, y):
        #BigWorld.logInfo(MOD_NAME, 'PanelView: as_setPositionS: ({}, {})'.format(x, y), None)
        self.flashObject.as_setPosition(x, y)

    def as_setValueS(self, name, value):
        #BigWorld.logInfo(MOD_NAME, 'PanelView: as_setValueS: ({}, {})'.format(name, value), None)
        self.flashObject.as_setValue(name, value)

    def as_getPanelSizeS(self):
        #BigWorld.logInfo(MOD_NAME, 'PanelView: as_getPanelSizeS', None)
        result = self.flashObject.as_getPanelSize()
        return result.width, result.height

    def setVisible(self, isVisible):
        BigWorld.logInfo(MOD_NAME, 'PanelView: setVisible: {}'.format(isVisible), None)
        self.flashObject.visible = isVisible


PANEL_VIEW_SETTINGS = ViewSettings(
    PANEL_VIEW_ALIAS,
    PanelView,
    PANEL_VIEW_SWF_FILE_PATH,
    ViewTypes.WINDOW,
    None,
    ScopeTemplates.DEFAULT_SCOPE
)
