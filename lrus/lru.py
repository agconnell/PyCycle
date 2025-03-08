'''Base class for LRUs'''
from abc import ABC, abstractmethod
import logging
import itertools
import sys
from datetime import datetime
import zmq


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

MAX_POINTS = 100


class LRU(ABC):
    '''Base class for anything that connects to the app'''
    def __init__(self, field):
        self.field = field
        self.points = []
        self.status = DISCONNECTED
        
        self.last_update = datetime.now().timestamp()
        self.retries = REQUEST_RETRIES

        logging.info("Connecting to server…")
        self.context = zmq.Context()
        self.client = self.context.socket(zmq.REQ)
        self.client.connect(SERVER_ENDPOINT)

    def set_status(self, status):
        '''Recieves a status update from the server and sets its own status'''
        # print(self.field, 'set status: ', status)
        self.status = int(status[FIELD_STATUS])

    @abstractmethod
    def measurement_handler(self, message):
        '''
        this will be called from the running 'real' lru as a callback when data come in
        '''

    @abstractmethod
    def get_value(self):
        '''gets the last updated value to be send to workout'''

    async def run(self):
        '''Start the LRU'''
        for _ in itertools.count():
            self.client.send_json(self.get_value())
            while self.status < DONE:
                if (self.client.poll(REQUEST_TIMEOUT) & zmq.POLLIN) != 0:
                    self.set_status(self.client.recv_json())
                    break

                self.retries -= 1
                logging.warning("%s: No response from server", __name__)
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

    