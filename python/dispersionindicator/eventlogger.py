
import logging
import os
import csv
from datetime import datetime

import BigWorld
from gui.battle_control import avatar_getter

from statsindicator import StatsIndicatorMeta
from mod_constants import MOD, LOG_DIR

_logger = logging.getLogger(MOD.NAME)

class EventLogger(StatsIndicatorMeta):
    def __init__(self, config, collector):
        super(EventLogger, self).__init__(collector)
        self.log_file = os.path.join(LOG_DIR, config['logfile'])
        self.names = config['items']
        self.header = self.names[:]
        self.header.insert(0, '# time')
        self.vehicleName = avatar_getter.getVehicleTypeDescriptor().type.name

    def start(self):
        _logger.info('%s.start', self.className)
        self.__strage = []
        if not os.path.isdir(LOG_DIR):
            _logger.info('%s.outputLog: make dir %s', self.className, LOG_DIR)
            os.makedirs(LOG_DIR)
        self.__file = open(self.log_file, 'ab', 0)
        self.__writer = csv.writer(self.__file, dialect='excel')
        self.__writer.writerow(['# vehicle={}'.format(self.vehicleName)])
        self.__writer.writerow(self.header)

    def stop(self):
        _logger.info('%s.stop', self.className)
        self.__file.close()

    def onEvent(self, reason):
        def getStatus(key):
            if key == 'eventName':
                return reason
            elif key == 'eventTime':
                return BigWorld.time()
            return getattr(self.vehicleStats, key, '')
        data = [ getStatus(key) for key in self.names ]
        data.insert(0, datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:23])
        self.__strage.append(data)
        self.__writer.writerow(data)
