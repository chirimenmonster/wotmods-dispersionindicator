
import logging
import os
import csv

import BigWorld

from statsindicator import StatsIndicatorMeta
from mod_constants import MOD, LOG_DIR

_logger = logging.getLogger(MOD.NAME)

class EventLogger(StatsIndicatorMeta):
    def __init__(self, config, collector):
        super(EventLogger, self).__init__(collector)
        self.log_file = os.path.join(LOG_DIR, 'event.log')
        self.names = ['time', 'distance', 'distanceH', 'distanceV', 'shotSpeed', 'shotSpeedH', 'shotSpeedV']

    def start(self):
        _logger.info('%s.start', self.className)
        self.__strage = []

    def stop(self):
        _logger.info('%s.stop', self.className)
        self.outputLog()

    def onEvent(self, reson):
        data = [ getattr(self.vehicleStats, key, '') for key in self.names ]
        data.insert(0, reson)
        self.__strage.append(data)

    def outputLog(self):
        if not os.path.isdir(LOG_DIR):
            _logger.info('%s.outputLog: make dir %s', self.className, LOG_DIR)
            os.makedirs(LOG_DIR)
        _logger.info('%s.outputEventLog: save file: %s, %s', self.className, self.log_file, len(self.__strage))
        with open(self.log_file, 'wb') as fp:
            writer = csv.writer(fp, dialect='excel')
            writer.writerow(['event'] + self.names)
            writer.writerows(self.__strage)
