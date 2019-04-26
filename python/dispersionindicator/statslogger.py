
import os
import csv

import BigWorld

from statsindicator import StatsIndicatorMeta
from mod_constants import MOD_NAME, LOG_FILE


class StatsLogger(StatsIndicatorMeta):
    def __init__(self, config, collector):
        super(StatsLogger, self).__init__(collector)
        statsdefs = config['statsDefs']
        self.names = [ statsdefs[key]['status'] for key in config['items'] ]

    def start(self):
        BigWorld.logInfo(MOD_NAME, '{}.start'.format(self.className), None)
        self.__strage = []

    def stop(self):
        BigWorld.logInfo(MOD_NAME, '{}.stop'.format(self.className), None)
        self.outputLog()
   
    def update(self):
        data = [ self.getStatus(key, 1.0) for key in self.names ]
        #BigWorld.logInfo(MOD_NAME, '{}.update: {}'.format(self.className, data), None)
        self.__strage.append(data)
    
    def outputLog(self):
        log_dir = os.path.dirname(LOG_FILE)
        if not os.path.isdir(log_dir):
            BigWorld.logInfo(MOD_NAME, '{}.outputLog: make dir {}'.format(self.className, log_dir), None)
            os.makedirs(log_dir)
        BigWorld.logInfo(MOD_NAME, '{}.outputLog: save file: {}, {}'.format(self.className, LOG_FILE, len(self.__strage)), None)
        with open(LOG_FILE, 'wb') as fp:
            writer = csv.writer(fp, dialect='excel')
            writer.writerow(self.names)
            writer.writerows(self.__strage)
