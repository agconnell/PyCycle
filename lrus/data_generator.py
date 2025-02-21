
import os
os.environ["PYTHONASYNCIODEBUG"] = str(1)
import asyncio
from datetime import datetime as dt
import argparse
import random
import zmq
import threading
import json

from lru import LRU, STOPPED, PAUSED, RUNNING, DONE

DISCONNECTED = 0
CONNECTED = 1


class DataGenerator(LRU):

    def __init__(self, field_name, workout_id=1):
        super().__init__()
        self.status = STOPPED
        self.start_time = dt.now().timestamp()
        self.uuid = workout_id
        self.field_name = field_name
        self.baseval = 100
        self.connected = False
        #0 not connected and 1 is connected
        self.last_dp = {'field': self.field_name, 'connection_state': DISCONNECTED}

        msg_thread = threading.Thread(target=self.recieve_msg)
        msg_thread.start()

    def recieve_msg(self):
        context = zmq.Context()
        client = context.socket(zmq.REQ)
        client.connect("tcp://localhost:5555")
        count = 0
        self.last_dp = {'field': self.field_name, 'connection_state': CONNECTED}
        while self.status < DONE:
            if count > 10 or self.connected == False:
                msg = json.dumps({'field': self.field_name, 'connected': self.connected})
                client.send_json(msg)
                count = 0
                self.connected = True
            else:
                self.connected = True
                msg = json.dumps(self.last_dp)
                client.send_json(msg)

            m = client.recv_string()
            self.status = int(m)


    def save_data(self, data):
        self.mongo.insert_data_point(data)

    async def mmeasurement_handler(self):
        val = self.baseval + random.randrange(-5, 5, 1)
        if self.status == PAUSED:
            print(f"DataGenerator {self.field_name} paused....: ")
        elif self.status == RUNNING:
            ts = round(dt.now().timestamp()-self.start_time)
            if ts > 3:
                # d = {'field': self.field_name, 'value': val, 'date': n, 'timestamp': ts, 'id': self.uuid}
                # self.save_data(d)
                self.last_dp = {'field': self.field_name, 'value': val}
        else:
            print(f"DataGenerator {self.field_name} not recording....: ")

    async def run(self):
        try:
            while self.status < DONE:
                # print(f"{self.field_name}: {self.status}")
                await self.mmeasurement_handler()
                await asyncio.sleep(0.5)
                    
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
    