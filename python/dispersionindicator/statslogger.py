
import logging
import os
import csv
from datetime import datetime

import BigWorld
from gui.battle_control import avatar_getter

from statsindicator import StatsIndicatorMeta
from mod_constants import MOD, LOG_DIR

_logger = logging.getLogger(MOD.NAME)

FILE_EXTENSION = '.csv'

class StatsLogger(StatsIndicatorMeta):
    def __init__(self, config, clientStatus):
        super(StatsLogger, self).__init__(config, clientStatus)
        self.names = config['items']
        self.header = self.names[:]
        self.header.insert(0, '# time')
        if 'logfile' in config:
            filename = config['logfile']
            self.openMode = 'ab'
        else:
            filename = datetime.now().strftime('%Y%m%d_%H%M_') + self.getStatus('vehicleName').replace(':', '-') + '_' + self.getStatus('arenaName') + FILE_EXTENSION
            self.openMode = 'wb'
        self.logFile = os.path.join(LOG_DIR, filename)

    def start(self):
        super(StatsLogger, self).start()
        self.__strage = []

    def stop(self):
        super(StatsLogger, self).stop()
        self.outputLog()
   
    def update(self):
        data = [ self.getStatus(key) for key in self.names ]
        data.insert(0, datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:23])
        self.__strage.append(data)
    
    def outputLog(self):
        if not os.path.isdir(LOG_DIR):
            _logger.info('%s.outputLog: make dir %s', self.className, LOG_DIR)
            os.makedirs(LOG_DIR)
        _logger.info('%s.outputLog: save file: %s, %s', self.className, self.logFile, len(self.__strage))
        with open(self.logFile, self.openMode) as fp:
            writer = csv.writer(fp, dialect='excel')
            writer.writerow(['# vehicle={} arena={}'.format(self.getStatus('vehicleName'), self.getStatus('arenaName'))])
            writer.writerow(self.header)
            writer.writerows(self.__strage)
