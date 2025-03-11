
'''Workout class that handles the workout data from the LRUs'''
import sys
import subprocess

import threading
import logging

from config.config import STOPPED, RUNNING, DONE
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
        logging.info("Received message: %s", message)
        self.messages += 1
        if self.messages == 10:
            self.status = STOPPED
        elif self.messages == 15:
            self.status = RUNNING
        elif self.messages > 25:
            self.status = DONE

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    server = TestServer()
    server_thread = threading.Thread(target=server.run)
    server_thread.start()

    python_executable = sys.executable
    # subprocess.Popen([python_executable, 'lrus/data_generator.py', 'rpm'])
    subprocess.Popen([python_executable, 'lrus/hrm.py', 'bpm'])
    
    # server_thread.join()