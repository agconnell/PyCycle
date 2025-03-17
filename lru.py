'''Base class for LRUs'''
from abc import ABC, abstractmethod
import logging
from datetime import datetime

from bleak import BleakClient, BleakScanner
import zmq

from config import DISCONNECTED, CONNECTED, FAILED, REQUEST_TIMEOUT
from config import FIELD_LRU, FIELD_NAME, FIELD_VALUE, FIELD_APP_STATUS, FIELD_LRU_STATUS
from config import SERVER_ENDPOINT


class LRU(ABC):
    '''Base class for anything that connects to the app'''
        
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


    def __init__(self, device_name, field_name):
        self.device_name = device_name
        self.field_name = field_name
        self.value = -1
        self.last_update = 0
        self.status = DISCONNECTED
        self.app_status = DISCONNECTED
        self.bleak_client = None

        logging.info("Connecting to server…")
        self.context = zmq.Context()
        self.zmq_client = self.context.socket(zmq.REQ)
        self.zmq_client.connect(SERVER_ENDPOINT)

    async def check_connection(self):
        '''update connection status based on timestamp of last update'''
        if self.last_update > REQUEST_TIMEOUT:
            self.status = DISCONNECTED
        LRU.logger.debug("Last BT update: %s", self.last_update)

    async def scan(self, device_name):
        '''Scans for the device with the given name'''
        LRU.logger.debug("Scanning for the device...")
        device = await BleakScanner.find_device_by_name(device_name)
        if not device:
            LRU.logger.error("Device %s not found.", device_name)
            # raise ConnectionError(f"Device {device_name} not found.")
        return device


    async def connect(self, address):
        '''Connects to the device with the given address'''
        self.bleak_client = BleakClient(address, timeout=REQUEST_TIMEOUT)

        try:
            await self.bleak_client.connect()
            if self.bleak_client.is_connected:
                LRU.logger.info("Connected to the device.")
                self.status = CONNECTED
        except Exception as e:
            LRU.logger.error("Unable to initiate connection to HRM:  %s", e)
            await self.disconnect()

    async def disconnect(self):
        '''Disconnects from the device'''
        await self.bleak_client.disconnect()
        self.zmq_client.send_json({FIELD_LRU: self.field_name, FIELD_LRU_STATUS: FAILED})
        self.zmq_client.close()

        LRU.logger.info("Disconnected from the device %s.", __name__)


    def set_app_status(self, status):
        '''Recieves a status update from the server and sets its own status'''
        self.app_status = int(status[FIELD_APP_STATUS])

    @abstractmethod
    def measurement_handler(self, message):
        '''
        this will be called from the running 'real' lru as a callback when data come in
        '''
    @abstractmethod
    async def run(self):
        '''Start the zmq client and run in loop'''

    def get_value(self):
        '''
        I have values as a list because might want to keep multiple values between
        calls to get values, but for now just return the last one
        '''
        logging.debug("DataGenerator 'get_value': %s", self.value)
        return  {FIELD_LRU: self.device_name, FIELD_LRU_STATUS: self.status, FIELD_NAME: self.field_name, FIELD_VALUE:  self.value}

    def _reconnect_zmq_client(self):
        '''Reconnects the ZMQ client'''
        self.zmq_client = self.context.socket(zmq.REQ)
        self.zmq_client.connect(SERVER_ENDPOINT)
        req = self.get_value()
        logging.info("Resending (%s)", req)
        self.zmq_client.send_json(req)

    def _handle_no_response(self):
        '''Handles the case when there is no response from the server'''
        logging.warning("%s: No response from server", __name__)
        self.zmq_client.setsockopt(zmq.LINGER, 0)
        self.zmq_client.close()
        logging.info("Reconnecting to server…")
        self._reconnect_zmq_client()
