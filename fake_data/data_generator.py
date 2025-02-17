
import os
os.environ["PYTHONASYNCIODEBUG"] = str(1)
import asyncio
from datetime import datetime as dt
import argparse
import random
import zmq

from mongo import Mongo

STOPPED = 0
RUNNING = 1
PAUSED = 2
UNPAUSE = 4
DONE = 3


class DataGenerator():

    def __init__(self, field_name, workout_id=1):
        self.RUNNING = True
        self.mongo = Mongo()
        self.start_time = dt.now().timestamp()
        self.client = None
        self.uuid = workout_id
        self.field_name = field_name
        self.baseval = 100
        self.paused = False

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect("tcp://localhost:5555")
        self.socket.subscribe("")
        self.status = STOPPED

    def connect(self):
        print('connect to DataGenerator')

    def to_time(self, secs):
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
 
    async def recieve_msg(self):
        m = self.socket.recv_string()
        self.status = int(m)
        if  self.status == UNPAUSE:
            self.start_time = dt.now().timestamp()

        # print(f'status {self.field_name}: {self.status}')

    async def mmeasurement_handler(self):
        val = self.baseval + random.randrange(-5, 5, 1)
        if self.status == PAUSED:
            print(f"DataGenerator {self.field_name} paused....: ")
        elif self.status == RUNNING:
            n = dt.now()
            ts = round(n.timestamp()-self.start_time)
            d = {'date': n, 'timestamp': ts, self.field_name: val, 'id': self.uuid}
            self.mongo.insert_data_point(d)
        else:
            print(f"DataGenerator {self.field_name} not recording....: ")

    async def run(self):
        try:
            while not self.status == DONE:
                await self.mmeasurement_handler()
                await self.recieve_msg()
                await asyncio.sleep(1)
                    
        except Exception as e:
            print(e)

        print(f'DataGenerator for {self.field_name} DONE!')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('field_name', type=str, help='field_name - like bpm, rpm or watts')
    parser.add_argument('id', type=str, help='workout id')
    id = parser.parse_args().id
    field_name = parser.parse_args().field_name
    dg = DataGenerator(field_name, id)
    
    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    dg.loop = asyncio.new_event_loop()
    dg.loop.run_until_complete(dg.run())
    