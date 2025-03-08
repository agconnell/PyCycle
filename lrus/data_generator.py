'''Fake LRU for Dev/Testing'''

import os
import asyncio
import argparse
import itertools
import logging
import sys
import random
from datetime import datetime

import zmq

from lru import LRU, FIELD_NAME, FIELD_VALUE, DONE, REQUEST_TIMEOUT, SERVER_ENDPOINT


class DataGenerator(LRU):
    '''This is a just for testing it generates fake data for dev/testing
       using this avoids having to connect any LRU to avoid connection issues
    '''
    def __init__(self, field):
        super().__init__(field)
        self.baseval = 100
        self.loop = None
        self.start_time = datetime.now().timestamp()
        print("starting data generator")


    def get_value(self):
        '''
        I have values as a list because might want to keep multiple values between
        calls to get values, but for now just return the last one
        '''
        if len(self.points) > 0:
            return  self.points[-1]
        else:
            return  {FIELD_NAME: self.field, FIELD_VALUE: 0}

    def measurement_handler(self, message):
        '''
        this will be called from the running 'real' lru as a callback when data come in
        '''
        print(f"DataGenerator 'handle_message': {message}")
        mag = {FIELD_NAME: self.field, FIELD_VALUE: message[self.field]}
        if self.status < DONE:
            self.points.append(mag)
        else:
            print("HeartRateMonitor not recording.... bpm: ", message[self.field])
 


    async def run(self):
        '''Start the LRU'''
        for _ in itertools.count():
            self.client.send_json(self.get_value())
            while self.status < DONE:
                if (self.client.poll(REQUEST_TIMEOUT) & zmq.POLLIN) != 0:
                    self.set_status(self.client.recv_json())
                    message = {self.field: self.baseval+random.randrange(-10, 10)}
                    self.measurement_handler(message)
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
            

 
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('field_name', type=str, help='field_name - like bpm, rpm or watts')
    field_name = parser.parse_args().field_name
    dg = DataGenerator(field_name)

    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    dg.loop = asyncio.new_event_loop()
    dg.loop.run_until_complete(dg.run())
