
import logging
import traceback

from gui.Scaleform.daapi.view.battle import shared as battle_shared

from mod_constants import MOD
from hook import overrideMethod
from statscollector import callOriginal
from view.panelview import PANEL_VIEW_SETTINGS

_logger = logging.getLogger(MOD.NAME)


@overrideMethod(battle_shared, 'getViewSettings')
@callOriginal(prev=True)
def getViewSettings(orig_result):
    _logger.info('getViewSettings')
    traceback.print_stack()
    #result = orig_result + (PANEL_VIEW_SETTINGS,)
    return orig_result


dummy = None
