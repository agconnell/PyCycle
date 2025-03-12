'''Fake LRU for Dev/Testing'''

import os
import sys
import asyncio
import argparse
import itertools
import random
from datetime import datetime
import logging
from zmq import POLLIN

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lrus.lru import LRU
from config.config import DONE, STOPPED, FIELD_NAME, FIELD_VALUE, REQUEST_TIMEOUT


class DataGenerator(LRU):
    '''This is a just for testing it generates fake data for dev/testing
       using this avoids having to connect any LRU to avoid connection issues
    '''
    def __init__(self, field):
        super().__init__(field)
        self.baseval = 100
        self.start_time = datetime.now().timestamp()
        self.points = []



    def measurement_handler(self, message):
        ''' this will be called from the running 'real' lru as a callback when data come in'''
        if self.status == STOPPED:
            logging.warning("DataGenerator not recording: %s", message)
        else:
            self.points.append(message[self.field])


    async def run(self):
        '''Start the LRU'''
        logging.info("running data generator")
        #this send is to innitiate the connection with the server
        self.zmq_client.send_json({FIELD_NAME: self.field, FIELD_VALUE: 0})

        for _ in itertools.count():
            while self.status < DONE:
                if (self.zmq_client.poll(REQUEST_TIMEOUT) & POLLIN) != 0:
                    self.set_status(self.zmq_client.recv_json())
                    message = {self.field: self.baseval+random.randrange(-10, 10)}
                    self.measurement_handler(message)
                    self.zmq_client.send_json(self.get_value())
                    # break




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('field_name', type=str, help='field_name - like bpm, rpm or watts')
    field_name = parser.parse_args().field_name
    dg = DataGenerator(field_name)

    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    dg.loop = asyncio.new_event_loop()
    dg.loop.run_until_complete(dg.run())
