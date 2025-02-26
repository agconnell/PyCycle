
import os
os.environ["PYTHONASYNCIODEBUG"] = str(1)
import asyncio
from datetime import datetime as dt
import argparse
import random

from lru import LRU, FIELD_NAME, FIELD_VALUE
from lru import DISCONNECTED, CONNECTED, RUNNING, PAUSED, STOPPED, DONE


class DataGenerator(LRU):

    def __init__(self, workout_id, field_name):
        super().__init__(workout_id, field_name)
        self.baseval = 100
        self.field_name = field_name
        print("starting data generator")

    def get_value(self):
        val = random.randrange(100, 125, 1)
        return  {FIELD_NAME: self.field, FIELD_VALUE: val}     
    
    async def mmeasurement_handler(self, message):
        print("DataGenerator 'handle_message': {message}")
    
    async def run(self):
        try:
            while self.status < DONE:
                print(f"{self.field_name}: {self.status}")
                await self.mmeasurement_handler(123)
                await asyncio.sleep(0.5)
                    
        except Exception as e:
            print(e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('id', type=str, help='workout id')
    parser.add_argument('field_name', type=str, help='field_name - like bpm, rpm or watts')
    id = parser.parse_args().id
    field_name = parser.parse_args().field_name
    dg = DataGenerator(id, field_name)
    
    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    dg.loop = asyncio.new_event_loop()
    dg.loop.run_until_complete(dg.run())
    