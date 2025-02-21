
import zmq
import datetime
import time
import logging


from zmq_base import DISCONNECTED, CONNECTED, DONE, CLIENT_ENDPOINT, TIMEOUT
from zmq_base import FIELD_ID, FIELD_STATUS, FIELD_NAME, FIELD_VALUE, FIELD_LAST_UPDATE

class LRU():    
    def __init__(self, id, field=None):
        self.id = id
        self.status = DISCONNECTED
        self.last_update = datetime.datetime.now().timestamp()
        self.field = FIELD_ID
        self.value = 0

    def get_data(self):
        return self.field, self.value,
    def set_data(self, message):
            setattr(self, FIELD_STATUS, CONNECTED)
            setattr(self, FIELD_LAST_UPDATE, datetime.datetime.now().timestamp())
            setattr(self, FIELD_VALUE, message[FIELD_VALUE])

class ZMQ_Server():
    lrus = {}
    status = DISCONNECTED

    def __init__(self, lrus_ids=[]):
        for id in lrus_ids:
            self.lrus[id] = LRU(id)

        context = zmq.Context()
        self.server = context.socket(zmq.REP)
        self.server.bind(CLIENT_ENDPOINT)
        self.star_time = datetime.datetime.now().timestamp()

    def handle_message(self, message):
        print(f'Server received: {message}')
        if FIELD_ID in message and message[FIELD_ID] in self.lrus:
            self.lrus[message[FIELD_ID]].set_data(message)
        else:
            logging.warning(f'Unknown LRU message: {message}')

    def check_status(self):
        cur_time = datetime.datetime.now().timestamp()
        for lru in self.lrus.values():
            if cur_time - lru.last_update > TIMEOUT:
                lru.status = DISCONNECTED
                logging.warning(f'LRU: {lru.id} is disconnected - last update: {lru.last_update}')

    def get_client(self, id):
        return self.lrus[id]

    def run(self):
        while self.status < DONE:
            #receive a message and handle it
            message = self.server.recv_json()
            self.handle_message(message)

            #check the status of the LRUs
            self.check_status()

            #send heartbeat 
            self.server.send_json({FIELD_STATUS: 1})
            
            #take a nap
            time.sleep(0.25)

            #do it all again
    