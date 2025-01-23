import asyncio
from bleak import BleakClient
from src.pm_service import CyclingPowerService


class PowerMeter():
    def __init__(self):
        self.kickr_address = "FB:4A:F1:1F:1B:73"

    def power_measurement_handler(self, measurement):
        print(f'power: {measurement.instantaneous_power}')

    async def connect_power_meter(self):
        print('connecting to power meter')
        pm = BleakClient(self.kickr_address)
        try:
            await pm.connect()
        except Exception as e:
            print(f'Error connecting to power meter: {e}')
            return None
        return pm

    async def start_power_meter(self, power_client):
        print('Recording power data')
        trainer = CyclingPowerService(power_client)
        trainer.set_cycling_power_measurement_handler(self.power_measurement_handler)
        await trainer.enable_cycling_power_measurement_notifications()
        while(True):
            await asyncio.sleep(1)
