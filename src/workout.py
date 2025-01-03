import asyncio
from bleak import BleakClient
from src.cycling_power_service import CyclingPowerService
from src.heart_rate_service import HeartRateService

class Workout():
    def __init__(self):
        self.hrm_address = "CB:E1:30:26:F4:EE"
        self.kickr_address = "FB:4A:F1:1F:1B:73"

    def power_measurement_handler(self, measurement):
        print(f'power: {measurement.instantaneous_power}')

    async def connect_power_meter(self):
        print('connecting to power meter')
        pm = BleakClient(self.kickr_address)
        await pm.connect()
        return pm

    async def start_power_meter(self, power_client):
        print('Recording power data')
        trainer = CyclingPowerService(power_client)
        trainer.set_cycling_power_measurement_handler(self.power_measurement_handler)
        await trainer.enable_cycling_power_measurement_notifications()
        while(True):
            await asyncio.sleep(1)



    def hrm_measurement_handler(self, measurement):
        print(f'hrm: {measurement.bpm}')

    async def connect_hrm(self):
        print('connecting to heart rate monitor')
        hrm = BleakClient(self.hrm_address)
        await hrm.connect()
        return hrm

    async def start_hrm(self, hrm_client):
        print('Recording hrm data')
        hrms = HeartRateService(hrm_client)
        hrms.set_hr_measurement_handler(self.hrm_measurement_handler)
        await hrms.enable_hr_measurement_notifications()
        while(True):
            await asyncio.sleep(1)



    def start_workout(self):
        print('starting workout')
        
        loop = asyncio.get_event_loop()

        power_client = loop.run_until_complete(self.connect_power_meter())
        hrm_client = loop.run_until_complete(self.connect_hrm())

        if power_client and power_client.is_connected:
            loop.create_task(self.start_power_meter(power_client))

        if hrm_client and hrm_client.is_connected:
            loop.create_task(self.start_hrm(hrm_client))
        
        loop.run_forever()
