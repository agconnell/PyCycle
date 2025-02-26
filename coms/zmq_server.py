
import zmq
import datetime
import time
import logging


from config.config import DISCONNECTED, DONE
from config.config import FIELD_STATUS, FIELD_ID, TIMEOUT

CLIENT_ENDPOINT = "tcp://*:5555"
    
class ZMQ_Server():
    status = DISCONNECTED

    def __init__(self, callback):

        context = zmq.Context()
        self.server = context.socket(zmq.REP)
        self.server.bind(CLIENT_ENDPOINT)
        self.handle_message = callback

    def check_status(self):
        cur_time = datetime.datetime.now().timestamp()
        for lru in self.lrus.values():
            if cur_time - lru.last_update > TIMEOUT:
                lru.status = DISCONNECTED
                logging.warning(f'LRU: {lru.id} is disconnected - last update: {lru.last_update}')

    def run(self):
        while self.status < DONE:
            #receive a message and handle it
            message = self.server.recv_json()
            self.handle_message(self, message)

            #check the status of the LRUs
            self.check_status()

            #send heartbeat 
            self.server.send_json({FIELD_STATUS: 1})
            
            #take a nap
            time.sleep(0.25)

            #do it all again
            print("zmq server running")