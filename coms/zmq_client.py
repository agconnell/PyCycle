
import zmq
import random
import itertools
import logging
import sys

from coms.zmq_base import REQUEST_TIMEOUT, REQUEST_RETRIES, SERVER_ENDPOINT, SERVER_ENDPOINT
from config.config import DISCONNECTED, DONE
from config.config import FIELD_ID, FIELD_NAME, FIELD_VALUE, FIELD_STATUS

class ZMQ_Client():

    def __init__(self, id, field):
        self.id = id
        self.field = field
        self.status = DISCONNECTED
        self.retries = REQUEST_RETRIES

        logging.info("Connecting to server…")
        self.context = zmq.Context()
        self.client = self.context.socket(zmq.REQ)
        self.client.connect(SERVER_ENDPOINT)

    def handle_message(self, message):
        if FIELD_STATUS in message:
            self.status = message[FIELD_STATUS]
            # logging.info(f'{self.id} set status: {self.status}')
        else:
            logging.error(f"can't handle message: {message}")
              
    def get_value(self):
        val = random.randrange(100, 125, 1)
        return  {FIELD_ID: self.id, FIELD_NAME: self.field, FIELD_VALUE: val}
    
  
    def _handle_no_response(self):
        '''Handles the case when there is no response from the server'''
        self.retries -= 1
        logging.warning("%s: No response from server", __name__)
        self.zmq_client.setsockopt(zmq.LINGER, 0)
        self.zmq_client.close()
        if self.retries == 0:
            logging.error("Server seems to be offline, abandoning")
            sys.exit()

        logging.info("Reconnecting to server…")
        self._reconnect_zmq_client()

    def _reconnect_zmq_client(self):
        '''Reconnects the ZMQ client'''
        self.zmq_client = self.context.socket(zmq.REQ)
        self.zmq_client.connect(SERVER_ENDPOINT)
        req = self.get_value()
        logging.info("Resending (%s)", req)
        self.zmq_client.send_json(req)

    async def run(self):
        '''Start the LRU'''
        for _ in itertools.count():
            self.zmq_client.send_json(self.get_value())
            while self.status < DONE:
                if (self.zmq_client.poll(REQUEST_TIMEOUT) & zmq.POLLIN) != 0:
                    self.set_status(self.zmq_client.recv_json())
                    break

                self.retries -= 1
                logging.warning("%s: No response from server", __name__)
                # Socket is confused. Close and remove it.
                self.zmq_client.setsockopt(zmq.LINGER, 0)
                self.zmq_client.close()
                if self.retries == 0:
                    logging.error("Server seems to be offline, abandoning")
                    sys.exit()

                logging.info("Reconnecting to server…")

                # Create new connection
                self.zmq_client = self.context.socket(zmq.REQ)
                self.zmq_client.connect(SERVER_ENDPOINT)
                req = self.get_value()
                logging.info("Resending (%s)", req)
                self.zmq_client.send_json(req)


