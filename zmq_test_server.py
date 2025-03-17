
'''Workout class that handles the workout data from the LRUs'''
import sys
import subprocess
from datetime import datetime
import threading
import logging
import time

from config import DISCONNECTED, CONNECTED, STOPPED, RUNNING, DONE, FAILED
from config import FIELD_LRU, FIELD_LRU_STATUS
from zmq_server import ZmqServer

class TestServer(ZmqServer):
    '''Workout class that handles the workout data from the LRUs'''

    def __init__(self):
        '''Initialize the TestServer'''
        super().__init__()
        self.num_messages = 0
        self.lrus = {"hrm": DISCONNECTED}

    def handle_lru_status(self, message):
        '''returns the status'''
        logging.info("ZMQ Server sees LRU: %s    STATUS: %s", message[FIELD_LRU], message[FIELD_LRU_STATUS])
        self.lrus[message[FIELD_LRU]] = message[FIELD_LRU_STATUS]

    def handle_message(self, message: dict):
        '''Handle the message from the client'''
        self.num_messages += 1
        et = self.to_time(datetime.now().timestamp() - self.start_time)
        logging.info("  App received --  message: %s  status: %s  count: %s  elapsed time: %s", message, self.status, self.num_messages, et)

        self.handle_lru_status(message)
        cumulative_status = 0
        for status in self.lrus.values():
            cumulative_status += status

        if cumulative_status == -1:
            self.status = DONE
        else:
            if self.num_messages == 5:
                self.status = STOPPED
            elif self.num_messages == 10:
                self.status = RUNNING
            elif self.num_messages == 45:
                self.status = RUNNING
            # elif self.num_messages > 19:
            #     self.status = DONE

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    server = TestServer()
    server_thread = threading.Thread(target=server.run)
    server_thread.daemon = True
    server_thread.start()

    PYTHON = sys.executable
    try:
        subprocess.Popen([PYTHON, 'hrm_copilot.py'])
        subprocess.Popen([PYTHON, 'data_generator.py', 'Power Meter', 'Watts'])
    except subprocess.SubprocessError as e:
        sys.exit(1)

    while server.status < DONE:
        time.sleep(1)

    server_thread.join()
    sys.exit(0)
