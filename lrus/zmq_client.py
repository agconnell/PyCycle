
'''Base class for an LRU -- Heartrate Monitor, PowerMeter etc.'''
import itertools
import logging
import sys
import zmq

from config.config import DISCONNECTED, DONE, REQUEST_TIMEOUT

REQUEST_RETRIES = 3
SERVER_ENDPOINT = "tcp://localhost:5555"


# seconds before a lru is disconnected
TIMEOUT = 5


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
        pass
    
    def run(self):        
        for sequence in itertools.count():
            
            self.client.send_json(self.get_value())

            while self.status < DONE:
                if (self.client.poll(REQUEST_TIMEOUT) & zmq.POLLIN) != 0:
                    reply = self.client.recv_json()
                    if type(reply) == dict:
                        logging.info("Server replied OK (%s)", reply)
                        self.retries = REQUEST_RETRIES
                        break
                    else:
                        logging.error("Malformed reply from server: %s", reply)
                        continue

                self.retries -= 1

                logging.warning("ZMQ_Client: No response from server")
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


