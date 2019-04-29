
import logging
import os
import csv

import BigWorld

from statsindicator import StatsIndicatorMeta
from mod_constants import MOD, LOG_FILE

_logger = logging.getLogger(MOD.NAME)

class StatsLogger(StatsIndicatorMeta):
    def __init__(self, config, collector):
        super(StatsLogger, self).__init__(collector)
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
        _logger.debug('%s.update: %s', self.className, data)
        self.__strage.append(data)
    
    def outputLog(self):
        log_dir = os.path.dirname(LOG_FILE)
        if not os.path.isdir(log_dir):
            _logger.info('%s.outputLog: make dir %s', self.className, log_dir)
            os.makedirs(log_dir)
        _logger.info('%s.outputLog: save file: %s, %s', self.className, LOG_FILE, len(self.__strage))
        with open(LOG_FILE, 'wb') as fp:
            writer = csv.writer(fp, dialect='excel')
            writer.writerow(self.names)
            writer.writerows(self.__strage)
