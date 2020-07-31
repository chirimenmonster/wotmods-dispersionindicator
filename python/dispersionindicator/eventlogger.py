
import logging
import os
import csv

import BigWorld
from gui.battle_control import avatar_getter

from statsindicator import StatsIndicatorMeta
from mod_constants import MOD, LOG_DIR, EVENT

_logger = logging.getLogger(MOD.NAME)

class EventLogger(StatsIndicatorMeta):
    def __init__(self, config, clientStatus):
        super(EventLogger, self).__init__(config, clientStatus)
        self.log_file = os.path.join(LOG_DIR, config['logfile'])
        self.names = config['items']
        self.header = self.names[:]
        self.header.insert(0, '#')
        self.vehicleName = avatar_getter.getVehicleTypeDescriptor().type.name
        self.acceptEvents = config['events']
        self.__file = None

    def start(self):
        super(EventLogger, self).start()
        self.__strage = []
        if not os.path.isdir(LOG_DIR):
            _logger.info('%s.outputLog: make dir %s', self.className, LOG_DIR)
            os.makedirs(LOG_DIR)
        self.__file = open(self.log_file, 'ab', 0)
        self.__writer = csv.writer(self.__file, dialect='excel')
        self.__writer.writerow(['# vehicle={}'.format(self.vehicleName)])
        self.__writer.writerow(self.header)

    def stop(self):
        super(EventLogger, self).stop()
        self.__file.close()
        self.__file = None

    def onEvent(self, reason):
        if self.__file is None:
            return
        if reason['eventName'] not in self.acceptEvents:
            return
        def getStatus(key):
            if key in ['eventName', 'eventTime']:
                return reason[key]           
            return getattr(self.vehicleStats, key, '')
        data = [ getStatus(key) for key in self.names ]
        data.insert(0, '')
        self.__strage.append(data)
        self.__writer.writerow(data)
