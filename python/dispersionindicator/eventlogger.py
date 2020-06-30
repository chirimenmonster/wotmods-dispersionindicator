
import logging
import os
import csv

import BigWorld
from gui.battle_control import avatar_getter

from statsindicator import StatsIndicatorMeta
from mod_constants import MOD, LOG_DIR

_logger = logging.getLogger(MOD.NAME)

class EventLogger(StatsIndicatorMeta):
    def __init__(self, config, collector):
        super(EventLogger, self).__init__(collector)
        self.log_file = os.path.join(LOG_DIR, 'event.log')
        self.names = ['distance', 'distanceH', 'distanceV', 'shotSpeed', 'shotSpeedH', 'shotSpeedV']
        self.header = [ '# event', 'time' ] + self.names
        self.vehicleName = avatar_getter.getVehicleTypeDescriptor().type.name

    def start(self):
        _logger.info('%s.start', self.className)
        self.__strage = []

    def stop(self):
        _logger.info('%s.stop', self.className)
        self.outputLog()

    def onEvent(self, reason):
        _logger.info('%s.onEvent: %s', self.className, reason)
        data = [ reason, BigWorld.time() ]
        data += [ getattr(self.vehicleStats, key, '') for key in self.names ]
        self.__strage.append(data)

    def outputLog(self):
        if not os.path.isdir(LOG_DIR):
            _logger.info('%s.outputLog: make dir %s', self.className, LOG_DIR)
            os.makedirs(LOG_DIR)
        _logger.info('%s.outputEventLog: add to file: %s (nrecords=%s)', self.className, os.path.abspath(self.log_file), len(self.__strage))
        with open(self.log_file, 'ab') as fp:
            writer = csv.writer(fp, dialect='excel')
            writer.writerow(['# vehicle={}'.format(self.vehicleName)])
            writer.writerow(self.header)
            writer.writerows(self.__strage)
