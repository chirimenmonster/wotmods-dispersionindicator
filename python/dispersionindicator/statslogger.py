
import logging
import os
import csv
from datetime import datetime

import BigWorld
from gui.battle_control import avatar_getter

from statsindicator import StatsIndicatorMeta
from mod_constants import MOD, LOG_DIR

_logger = logging.getLogger(MOD.NAME)

class StatsLogger(StatsIndicatorMeta):
    def __init__(self, config, clientStatus):
        super(StatsLogger, self).__init__(config, clientStatus)
        self.log_file = os.path.join(LOG_DIR, config['logfile'])
        statsdefs = config['statsDefs']
        #self.names = [ statsdefs[key]['status'] for key in config['items'] ]
        self.names = config['items']
        self.header = self.names[:]
        self.header.insert(0, '# time')
        self.vehicleName = avatar_getter.getVehicleTypeDescriptor().type.name

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
        _logger.info('%s.outputLog: save file: %s, %s', self.className, self.log_file, len(self.__strage))
        with open(self.log_file, 'ab') as fp:
            writer = csv.writer(fp, dialect='excel')
            writer.writerow(['# vehicle={}'.format(self.vehicleName)])
            writer.writerow(self.header)
            writer.writerows(self.__strage)
