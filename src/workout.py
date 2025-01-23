import asyncio
from concurrent.futures import ProcessPoolExecutor
import time

from bleak import BleakClient

from src.hrm_service import HeartRateService

from src.hrm import HRM

class Workout():
    def __init__(self):
        pass

    async def connect_hrm(self):
        loop = asyncio.get_running_loop()
        exe = ProcessPoolExecutor(4)
        hrm = HRM()
        awaitable1 = loop.run_in_executor(exe, hrm.connect_hrm)
        await awaitable1
            


    def start_workout(self):
        print('starting workout')
