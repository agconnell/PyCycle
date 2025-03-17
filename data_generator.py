'''Fake LRU for Dev/Testing'''

import os
import sys
import asyncio
import argparse
import random
from datetime import datetime

from config import DISCONNECTED, CONNECTED, DONE, SLEEP_TIME
from config import FIELD_NAME, FIELD_VALUE
from lru import LRU

BASEVAL = 100

class DataGenerator(LRU):
    '''This is a just for testing it generates fake data for dev/testing
       using this avoids having to connect any LRU to avoid connection issues
    '''
    def __init__(self, device_name, field_name):
        super().__init__(device_name, field_name)
        self.device_name = device_name
        self.field_name = field_name
        self.status = DISCONNECTED
        self.num_bt_messages = 0

    async def connect(self, address):
        '''data generator needs to override this and spoof a connection'''
        LRU.logger.info("Connected to the device.")
        self.status = CONNECTED


    async def run(self):
        '''Start the LRU'''

        try:
            #scan for the device and connect not needed for fake lru
            await self.connect(None)
            LRU.logger.debug("running data generator")
            self.zmq_client.send_json(self.get_value())
            await asyncio.sleep(1)
            self.zmq_client.recv_json()
        except (ConnectionError, TypeError) as e:
            LRU.logger.error("Unable to initiate connection to HRM:  %s", e)


        try:
            while self.status < DONE:
                await self.check_connection()
                message = {self.field_name: BASEVAL+random.randrange(-10, 10)}
                self.measurement_handler(message)
                await asyncio.sleep(SLEEP_TIME)

        except Exception as e:
            LRU.logger.error("No connection to %s:  %s", self.device_name, e)

        finally:
            LRU.logger.info("Disconnected from the %s.", self.device_name)
            sys.exit(0)
            

    def measurement_handler(self, message):
        '''Handles the HR measurement data'''
        LRU.logger.debug('    data_generator fake msg: %s bpm', message)
        self.value = message[self.field_name]
        self.last_update = datetime.now().timestamp()
        self.num_bt_messages += 1
        self.zmq_client.send_json(self.get_value())
        self.set_app_status(self.zmq_client.recv_json())

    async def start(self):
        '''Starts the heart rate monitor'''
        await self.run()


if __name__ == "__main__":
    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    parser = argparse.ArgumentParser()
    parser.add_argument('lru', type=str, help='lru - device name like HRM or Power Meter')
    parser.add_argument('field_name', type=str, help='field_name - like bpm, rpm or watts')
    fn = parser.parse_args().field_name
    lru = parser.parse_args().lru
    dg = DataGenerator(lru, fn)

    asyncio.run(dg.start())
    sys.exit(0)