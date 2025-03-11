import asyncio
from bleak import BleakClient

from pycycling.heart_rate_service import HeartRateService


async def run(address):
    i = 0
    async with BleakClient(address) as client:
        def my_measurement_handler(data):
            print(f'HR: {data.bpm}')

        await client.is_connected()
        hr_service = HeartRateService(client)
        hr_service.set_hr_measurement_handler(my_measurement_handler)

        await hr_service.enable_hr_measurement_notifications()
        while True:
            await asyncio.sleep(0.25)
            i += 1

            if i == 100:
                print("disabling notifications")
                await hr_service.disable_hr_measurement_notifications()
                exit(0)


if __name__ == "__main__":
    import os

    os.environ["PYTHONASYNCIODEBUG"] = str(1)

    device_address = "CB:E1:30:26:F4:EE" #arm hrm -> "CB:E1:30:26:F4:EE" garmin hrm -> "E6:8E:30:CB:86:5E"
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(device_address))
