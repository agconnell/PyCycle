'''Base class for LRUs'''
from abc import ABC, abstractmethod
import logging
import sys
from datetime import datetime
import zmq

from config.config import DISCONNECTED


# message properties
FIELD_ID = 'id'
FIELD_NAME = 'field'
FIELD_VALUE = 'value'
FIELD_STATUS = 'status'
FIELD_LAST_UPDATE = 'last_update'

REQUEST_TIMEOUT = 5000
REQUEST_RETRIES = 3
SLEEP_TIME = 0.5
SERVER_ENDPOINT = "tcp://localhost:5555"
MAX_POINTS = 5


class LRU(ABC):
    '''Base class for anything that connects to the app'''
    def __init__(self, field):
        self.field = field
        self.points = []
        self.status = DISCONNECTED
        self.loop = None
        
        self.last_update = datetime.now().timestamp()
        self.retries = REQUEST_RETRIES


        logging.info("Connecting to server…")
        self.context = zmq.Context()
        self.zmq_client = self.context.socket(zmq.REQ)
        self.zmq_client.connect(SERVER_ENDPOINT)

    def to_time(self, secs):
        '''converts seconds into a time format for display 
            like 90 seconds --> 1:30'''
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

    @abstractmethod
    async def run(self):
        '''Start the zmq client and run in loop'''

    def _reconnect_zmq_client(self):
        '''Reconnects the ZMQ client'''
        self.zmq_client = self.context.socket(zmq.REQ)
        self.zmq_client.connect(SERVER_ENDPOINT)
        req = self.get_value()
        logging.info("Resending (%s)", req)
        self.zmq_client.send_json(req)

    def _handle_no_response(self):
        '''Handles the case when there is no response from the server'''
        self.retries -= 1
        logging.warning("%s: No response from server", __name__)
        self.zmq_client.setsockopt(zmq.LINGER, 0)
        self.zmq_client.close()
        if self.retries == 0:
            logging.error("ZMQ Server seems to be offline, abandoning")
            sys.exit()

        logging.info("Reconnecting to server…")
        self._reconnect_zmq_client()
