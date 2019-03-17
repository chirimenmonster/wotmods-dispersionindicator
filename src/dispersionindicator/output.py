
import os
import csv

import BigWorld
import GUI
from gui import g_guiResetters

from constants import MOD_NAME, LOG_FILE


class IndicatorLogger(object):
    def __init__(self, config, stats):
        self.stats = stats
        self.statsdefs = config['stats_defs']
        self.names = [ self.statsdefs[key]['status'] for key in config['items'] ]

    def start(self):
        BigWorld.logInfo(MOD_NAME, 'output.start', None)
        self.__strage = []

    def stop(self):
        BigWorld.logInfo(MOD_NAME, 'output.stop', None)
        self.outputLog()
   
    def update(self):
        data = [ getattr(self.stats, key, '') for key in self.names ]
        BigWorld.logInfo(MOD_NAME, 'stock data: {}'.format(data), None)
        self.__strage.append(data)
    
    def outputLog(self):
        log_dir = os.path.dirname(LOG_FILE)
        if not os.path.isdir(log_dir):
            BigWorld.logInfo(MOD_NAME, 'make dir {}'.format(log_dir), None)
            os.makedirs(log_dir)
        BigWorld.logInfo(MOD_NAME, 'output file: {}, {}'.format(LOG_FILE, len(self.__strage)), None)
        with open(LOG_FILE, 'wb') as fp:
            writer = csv.writer(fp, dialect='excel')
            writer.writerow(self.names)
            writer.writerows(self.__strage)
