'''Heart rate monitor instance of an LRU'''
import asyncio
import os
import sys
from datetime import datetime

from pycycling.heart_rate_service import HeartRateService

from config import DISCONNECTED, DONE, SLEEP_TIME
from config import FIELD_NAME, FIELD_VALUE, FIELD_APP_STATUS, FIELD_LRU_STATUS
from lru import LRU


class HeartRateMonitor(LRU):
    '''Heart rate monitor class'''
    
    def __init__(self, device_name, field_name):
        super().__init__(device_name, field_name)
        self.device_name = device_name
        self.field_name = field_name
        self.status = DISCONNECTED
        self.num_bt_messages = 0

    async def run(self):
        '''Runs the heart rate monitor'''
        try:
            LRU.logger.debug("Connecting to ZMQ server...")
            self.zmq_client.send_json(self.get_value())
            await asyncio.sleep(1)
            self.zmq_client.recv_json()

            device = await self.scan(self.device_name)
            await self.connect(device)
        except (ConnectionError, TypeError) as e:
            LRU.logger.error("Unable to initiate connection to HRM:  %s", e)

        try:
            hr_service = HeartRateService(self.bleak_client)
            hr_service.set_hr_measurement_handler(self.measurement_handler)
            await hr_service.enable_hr_measurement_notifications()
            LRU.logger.debug("HR measurement notifications enabled.")

            while self.status < DONE:
                await self.check_connection()
                await asyncio.sleep(SLEEP_TIME)

        except Exception as e:
            LRU.logger.error("No connection  to %s:  %s", self.device_name, e)

        finally:
            if self.bleak_client:
                await self.bleak_client.disconnect()
                hr_service = None
            
            LRU.logger.info("Disconnected from the device.")
            sys.exit(0)


    def measurement_handler(self, message):
        '''Handles the HR measurement data'''
        LRU.logger.debug('    HR: %s bpm', message.bpm)
        self.value = message.bpm
        self.last_update = datetime.now().timestamp()
        self.num_bt_messages += 1
        self.zmq_client.send_json(self.get_value())
        self.set_app_status(self.zmq_client.recv_json())

    async def start(self):
        '''Starts the heart rate monitor'''
        await self.run()

if __name__ == "__main__":
    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    hrm = HeartRateMonitor('HW706-0020070', 'bpm')
    asyncio.run(hrm.start())
    sys.exit(0)