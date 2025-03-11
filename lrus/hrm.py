
'''class for connecting to a bluetooth heart rate monitor
and sending the data to the workout class'''
import os
import sys
import asyncio
from datetime import datetime as dt
import argparse
import logging

from bleak import BleakClient, BleakScanner
from pycycling.heart_rate_service import HeartRateService
import zmq

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lrus.lru import LRU
from config.config import DISCONNECTED, DONE, STOPPED, FIELD_NAME, FIELD_VALUE, REQUEST_TIMEOUT


os.environ["PYTHONASYNCIODEBUG"] = str(1)
BPM_INDEX = 1
NUM_RETRIES = 5

class HeartRateMonitor(LRU):
    '''HRM class'''
    def __init__(self, field):
        super().__init__(field)
        self.device_address = "CB:E1:30:26:F4:EE" # arm hrm "CB:E1:30:26:F4:EE"
        self.start_time = dt.now().timestamp()
        bleak_client = None
        self.hr_service = None
        self.points = []

    def get_value(self):
        '''
        I have values as a list because might want to keep multiple values between
        calls to get values, but for now just return the last one
        '''
        if len(self.points) > 0:
            logging.info("HeartRateMonitor 'get_value': %s", self.points)
            avg = int(sum(self.points)/len(self.points))
            self.points = []
            return  avg
        else:
            return  0


    def measurement_handler(self, message):
        '''receives a message from a HRM and updates the list of values for that HRM'''
        print("measurement_handler")

    async def scan(self, device_name):
        '''scans for the device with the given name'''
        return await BleakScanner.find_device_by_name(device_name)

    async def run(self):
        #this send is to innitiate the connection with the server
        self.zmq_client.send_json({FIELD_NAME: self.field, FIELD_VALUE: 0})
        dev = await self.scan('HW706-0020070')
        async with BleakClient(dev, timeout=5) as bleak_client:
            try:

                def handler(message):
                    '''receives a message from a HRM and updates the list of values for that HRM'''
                    if self.status == STOPPED:
                        msg = {FIELD_NAME: self.field, FIELD_VALUE: message[BPM_INDEX]}
                        logging.warning("HeartRateMonitor not recording: %s", msg)
                    else:
                        self.points.append(message[BPM_INDEX])

                self.hr_service = HeartRateService(bleak_client)
                self.hr_service.set_hr_measurement_handler(handler)
                await self.hr_service.enable_hr_measurement_notifications()

                while self.status < DONE :
                    if (self.zmq_client.poll(REQUEST_TIMEOUT) & zmq.POLLIN) != 0:
                        self.set_status(self.zmq_client.recv_json())
                        if bleak_client.is_connected:
                            self.zmq_client.send_json(self.get_value())
                        else:
                            logging.warning("HRM disconnected")
                    else:
                        print("No response from server")
                        self._handle_no_response()
                    await asyncio.sleep(1.0)

            except Exception as e:
                if self.retries > 0:
                    self.retries -= 1
                    logging.warning("Error: %s - Retrying %s more times", e, self.retries)
                    await self.run()
                else:
                    print(f"Error: {e} - No more retries")
                    self.status = DONE

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('field_name', type=str, help='field_name - like bpm, rpm or watts')
    field_name = parser.parse_args().field_name
    hrm = HeartRateMonitor(field_name)
    
    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    hrm.loop = asyncio.new_event_loop()
    hrm.loop.run_until_complete(hrm.run())
    