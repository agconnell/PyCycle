
import os
import asyncio
from bleak import BleakClient

from pycycling.cycling_power_service import CyclingPowerService
from mongo import Mongo


KICKR_DEVICE_ADDRESS = "FB:4A:F1:1F:1B:73"
ERROR_TIMEOUT = 10
ASYNC_TIMEOUT = 20

class Kickr:

    def __init__(self, address):
        self.address = address
        self.trainer = None
        self.client = None
        self.mongo = Mongo()

    async def disconnect(self):
        await self.client.disconnect()

    async def connect(self):
        async with BleakClient(self.address, timeout=ASYNC_TIMEOUT) as self.client:
            self.client.is_connected()
            self.trainer = CyclingPowerService(self.client)
            self.trainer.set_cycling_power_measurement_handler(self.measurement_handler)


    async def measurement_handler(self, data):
        Mongo.insert_hr_data_point(data)

    async def update_status(self):
            await self.trainer.enable_cycling_power_measurement_notifications()
            await asyncio.sleep(30.0)
            await self.trainer.disable_cycling_power_measurement_notifications()

    async def stop(self):
        while self.client.is_connected():
            quit = input("Would you like to disconnect? (y/n): ")
            if quit == "y":
                await self.disconnect()
                break

    async def main(self):
        await self.connect()
        status_task = asyncio.to_thread(self.update_status())
        # quit_task = asyncio.stop()
        await self.disconnect()

if __name__ == "__main__":

    os.environ["PYTHONASYNCIODEBUG"] = str(1)

    kickr = Kickr(KICKR_DEVICE_ADDRESS)
    asyncio.run(kickr.main())
    
