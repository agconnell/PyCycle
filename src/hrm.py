import asyncio
from bleak import BleakClient
from src.hrm_service import HeartRateService

class HRM():
    def __init__(self):
        self.hrm_address = "CB:E1:30:26:F4:EE"

    def hrm_measurement_handler(self, measurement):
        print(f'hrm: {measurement.bpm}')

    async def connect_hrm(self):
        async with BleakClient(self.hrm_address) as client:
            def my_measurement_handler(data):
                print(f'HR: {data.bpm}')

            await client.is_connected()
            hr_service = HeartRateService(client)
            hr_service.set_hr_measurement_handler(my_measurement_handler)

            await hr_service.enable_hr_measurement_notifications()
            await asyncio.sleep(30.0)
            await hr_service.disable_hr_measurement_notifications()



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
