import asyncio
from datetime import datetime

from src.heart_rate_service import HeartRateService
from src.cycling_power_service import CyclingPowerService

from src.mongo import Mongo

class Interval():
    def __init__(self):
        
        self.duration = 30*60   # 30 minute workout in seconds

        self.power_min = 0  #0 watts
        self.power_max = 2000 #max kickr watts

        self.hr_min = 0 # bottom zone 2
        self.hr_max = 0

        self.gradient = 0
        self.wind_speed = 0

class Workout():
    def __init__(self):
        self.hrm_address = "CB:E1:30:26:F4:EE"
        self.kickr_address = "FB:4A:F1:1F:1B:73"
        self.intervals = []
        self.duration = 20*60
        self.name = ''
        self.description = ''
        self.running = False
        self.run_time = 0
        self.mongo = Mongo()

    async def start_hrm(self):
        i = 0
        while self.running:
            print(f"loop 2 - {i}")
            await asyncio.sleep(1)
            i += 1
        return


    async def start_power_meter(self):
        i = 0
        while self.running:
            print(f"loop 1 - {i}")
            await asyncio.sleep(1)
            i += 1
        return

    async def tick(self):
        while self.running:
            self.run_time += 1
            print(f'tick {self.run_time}')
            if self.run_time >= self.duration:
                await asyncio.create_task(self.stop_workout())
                print('workout complete')
            elif self.running == False:
                print('workout paused')
            else:
                await asyncio.sleep(1)

    def start_workout(self):
        print('starting workout')
        self.running = True
        loop = asyncio.get_event_loop()
        loop.create_task(self.start_hrm())
        loop.create_task(self.start_power_meter())
        loop.run_forever()

    async def stop_workout(self):
        print('stopping workout')
        self.running = False
        #todo: save and exit the workout

    async def pause_workout(self):
        if self.running == True:
            print('pausing workout')
            self.running = False
        else:
            print('unpaused workout')
            self.running = True
            await self.tick()
