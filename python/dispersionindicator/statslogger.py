
import logging
import os
import csv

import BigWorld

from statsindicator import StatsIndicatorMeta
from mod_constants import MOD, LOG_DIR

_logger = logging.getLogger(MOD.NAME)

class StatsLogger(StatsIndicatorMeta):
    def __init__(self, config, collector):
        super(StatsLogger, self).__init__(collector)
        self.log_file = os.path.join(LOG_DIR, config['logfile'])
        statsdefs = config['statsDefs']
        self.names = [ statsdefs[key]['status'] for key in config['items'] ]

    def start(self):
        _logger.info('%s.start', self.className)
        self.__strage = []

    def stop(self):
        _logger.info('%s.stop', self.className)
        self.outputLog()
   
    def update(self):
        data = [ self.getStatus(key, 1.0) for key in self.names ]
        #_logger.debug('%s.update: %s', self.className, data)
        self.__strage.append(data)
    
    def outputLog(self):
        if not os.path.isdir(LOG_DIR):
            _logger.info('%s.outputLog: make dir %s', self.className, LOG_DIR)
            os.makedirs(LOG_DIR)
        _logger.info('%s.outputLog: save file: %s, %s', self.className, self.log_file, len(self.__strage))
        with open(self.log_file, 'ab') as fp:
            writer = csv.writer(fp, dialect='excel')
            writer.writerow(self.names)
            writer.writerows(self.__strage)
