
import os
os.environ["PYTHONASYNCIODEBUG"] = str(1)
import asyncio
import zmq
from datetime import datetime as dt
import argparse
from bleak import BleakClient

from pycycling.heart_rate_service import HeartRateService
from mongo import Mongo

DONE = 'done'
PAUSE = 'pause'
RECORDING = True

class HeartRateMonitor():

    def __init__(self, workout_id=1):
        self.device_address = "CB:E1:30:26:F4:EE" # arm hrm "CB:E1:30:26:F4:EE"
        self.RUNNING = True
        self.mongo = Mongo()
        self.start_time = dt.now().timestamp()
        self.client = None
        self.hr_service = None
        self.uuid = workout_id
        # self.context = zmq.Context()
        # self.socket = self.context.socket(zmq.PAIR)
        # self.socket.connect("tcp://localhost:1234")

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
    
    async def check_pause(self):
        # print("w1 check if done")
        if os.path.exists(PAUSE):
            print("HeartRateMonitor paused")
            RECORDING = False      

    async def check_done(self):
        # print("w1 check if done")
        if os.path.exists(DONE):
            self.RUNNING = False
            print("HeartRateMonitor done")
            # self.socket.send_string("HeartRateMonitor check done")
            await self.hr_service.disable_hr_measurement_notifications()
            self.loop.stop()          
    
    def mmeasurement_handler(self, data):
        if RECORDING:
            n = dt.now()
            ts = round(n.timestamp()-self.start_time)
            d = {'date': n, 'timestamp': ts,'bpm': data.bpm, 'id': self.uuid}
            self.mongo.insert_data_point(d)
        else:
            print("HeartRateMonitor not recording.... bpm: ", data.bpm)

    async def run(self):
        try:
            async with BleakClient(self.device_address) as self.client:
                self.hr_service = HeartRateService(self.client)
                self.hr_service.set_hr_measurement_handler(self.mmeasurement_handler)
                await self.hr_service.enable_hr_measurement_notifications()
                if self.client.is_connected:
                    while self.RUNNING:
                        await self.check_done()
                        await self.check_pause()
                        await asyncio.sleep(1)
                    
        except Exception as e:
            print(e)
            # self.callback('Error: ' + str(e))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('id', type=str, help='workout id')
    id = parser.parse_args().id
    hrm = HeartRateMonitor(id)
    
    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    hrm.loop = asyncio.new_event_loop()
    hrm.loop.run_until_complete(hrm.run())
    