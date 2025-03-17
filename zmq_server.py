'''
This module contains the ZMQ_Server class that is the base class for the workout 
that sends and receives messages from the LRUs'''
import time
from abc import ABC, abstractmethod
import logging
from datetime import datetime


import zmq

from config import DISCONNECTED, DONE, SOCKET_TIMEOUT
from config import FIELD_APP_STATUS, FIELD_LRU_STATUS

CLIENT_ENDPOINT = "tcp://*:5555"
SLEEP_INTERVAL = 0.5

class ZmqServer(ABC):
    '''Base class for the workout that sends and receives messages from the LRUs'''
    status = DISCONNECTED

    def __init__(self):

        context = zmq.Context()
        self.socket = context.socket(zmq.REP)
        self.socket.bind(CLIENT_ENDPOINT)
        self.start_time = datetime.now().timestamp()

    # @abstractmethod
    # def handle_lru_status(self, message):
    #     '''returns the status'''

    @abstractmethod
    def handle_message(self, message):
        '''handle the message from the client'''
    
    def to_time(self, secs):
        '''converts seconds into a time format for display like 90 seconds --> 1:30'''
        secs = round(secs)
        h = 0
        m = 0
        s = 0
        if secs > 3600:
            h = int(secs / 3600)
            secs = secs - h * 3600
        if secs > 59:
            m = int(secs / 60)
            secs = secs - (m * 60)
        s = secs

        if h == 0:
            return f"{m:02}:{s:02}"
        else:
            return f"{h:02}:{m:02}:{s:02}"
        
    def run(self):
        '''start the zmq server'''
        logging.debug("Start ZMQ server")
        poller = zmq.Poller()
        poller.register(self.socket, zmq.POLLIN)
        
        while self.status < DONE:
            try:
                #receive a message and handle it
                if poller.poll(SOCKET_TIMEOUT):
                    logging.debug("ZMQ Socket connected")
                    message = self.socket.recv_json()
                    self.handle_message(message)

                    #send heartbeat
                    self.socket.send_json({FIELD_APP_STATUS: self.status})
                    time.sleep(SLEEP_INTERVAL)
                else:
                    logging.error("Socket timed out connecting to device")
                    self.status = DONE
                    raise zmq.ZMQError("Socket timed out connecting to device(s).  Make sure they are on")
            except zmq.ZMQError as e:
                logging.error("ZMQ error in ZMQ server: %s", e)
                break
            except ValueError as e:     #TODO value and system errror prob not useful
                logging.error("Value error in ZMQ server: %s", e)
                break
            except SystemError as e:
                logging.error("Unexpected error in ZMQ server: %s", e)
                break

        self.socket.close()
        return