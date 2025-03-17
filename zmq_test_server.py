
'''Workout class that handles the workout data from the LRUs'''
import sys
import subprocess

import threading
import logging

from config.config import CONNECTED, STOPPED, RUNNING, DONE
from coms.zmq_server import ZmqServer

class TestServer(ZmqServer):
    '''Workout class that handles the workout data from the LRUs'''

    def __init__(self):
        '''Initialize the TestServer'''
        super().__init__()
        self.messages = 0

    def check_lru_status(self):
        '''Check the status of the LRUs'''
        pass

    def handle_message(self, message: dict):
        '''Handle the message from the client'''
        self.messages += 1
        logging.info("ZMQ Server Received --  message: %s  status: %s   count: %s", message, self.status, self.messages)
        if self.messages == 5:
            self.status = CONNECTED
        elif self.messages == 10:
            self.status = STOPPED
        elif self.messages == 15:
            self.status = RUNNING
        elif self.messages > 19:
            self.status = DONE

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    server = TestServer()
    server_thread = threading.Thread(target=server.run)
    server_thread.start()

    python_executable = sys.executable
    # subprocess.Popen([python_executable, 'lrus/data_generator.py', 'rpm'])
    subprocess.Popen([python_executable, 'lrus/hrm.py', 'bpm'])
    
    server_thread.join()