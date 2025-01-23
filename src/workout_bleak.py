
from src.hrm_service import HeartRateService
from src.pm_service import CyclingPowerService

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

    def add_interval(self, interval):
        self.intervals.append(interval)

    async def start_hrm(self):
        async with BleakClient(self.hrm_address) as client:
            def my_measurement_handler(data):
                print(f'HR: {data.bpm}')

            await client.is_connected()
            hr_service = HeartRateService(client)
            hr_service.set_hr_measurement_handler(my_measurement_handler)

            await hr_service.enable_hr_measurement_notifications()
            await asyncio.sleep(self.duration)
            # await hr_service.disable_hr_measurement_notifications()


    async def start_power_meter(self):
        print('connecting to power meter')
        async with BleakClient(self.kickr_address, timeout=20) as power_client:
            await power_client.is_connected()
            print('connected to power meter')
            trainer = CyclingPowerService(power_client)
            trainer.set_cycling_power_measurement_handler(self.mongo.insert_power_data_point)

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



    #todo: implement a timer that will check if it's time to change the interval
