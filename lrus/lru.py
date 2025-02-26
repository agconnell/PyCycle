'''Base class for LRUs'''
from abc import ABC, abstractmethod
import logging
import itertools
import sys
import zmq
from datetime import datetime

from zmq_client import ZMQ_Client

# Application States
DISCONNECTED = 0
CONNECTED = 1
STOPPED = 2
RUNNING = 3
PAUSED = 4
DONE = 5


# message properties
FIELD_ID = 'id'
FIELD_NAME = 'field'
FIELD_VALUE = 'value'
FIELD_STATUS = 'status'
FIELD_LAST_UPDATE = 'last_update'

REQUEST_TIMEOUT = 5000
REQUEST_RETRIES = 3
SERVER_ENDPOINT = "tcp://localhost:5555"


class LRU(ABC):

    def __init__(self, id, field):
        self.status = DISCONNECTED
        self.id = id
        self.field = field
        self.value = 0
        self.last_update = datetime.now().timestamp()

        logging.info("Connecting to server…")
        self.context = zmq.Context()
        self.client = self.context.socket(zmq.REQ)
        self.client.connect(SERVER_ENDPOINT)

    def set_status(self, status):
        '''Recieves a status update from the server and sets its own status'''
        self.status = status

    @abstractmethod
    def mmeasurement_handler(self, message):
        '''handles incoming data from LRU (hrm/power meter/etc.) and sets
        it to it's current value then sent to the server off cycle from being updated from LRU'''
        pass

    def run(self):        
        for sequence in itertools.count():
            
            self.client.send_json(self.get_value())

            while self.status < DONE:
                if (self.client.poll(REQUEST_TIMEOUT) & zmq.POLLIN) != 0:
                    self.status = self.client.recv_json()

                self.retries -= 1

                logging.warning("No response from server")
                # Socket is confused. Close and remove it.
                self.client.setsockopt(zmq.LINGER, 0)
                self.client.close()
                if self.retries == 0:
                    logging.error("Server seems to be offline, abandoning")
                    sys.exit()

                logging.info("Reconnecting to server…")

                # Create new connection
                self.client = self.context.socket(zmq.REQ)
                self.client.connect(SERVER_ENDPOINT)
                req = self.get_value()
                logging.info("Resending (%s)", req)
                self.client.send_json(req)

    def to_time(self, secs):
        secs = round(secs)
        h = 0
        m = 0
        s = 0
        if secs > 3600:
            h = int(secs / 3600)
            secs = secs - h * 3600
        if secs > 59:
            m = int(secs / 60)
            secs = secs - (m * 60)    
        s = secs

        if h == 0:
            return f"{m:02}:{s:02}"
        else:
            return f"{h:02}:{m:02}:{s:02}"
 

        pass