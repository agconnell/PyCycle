'''
This module contains the ZMQ_Server class that is the base class for the workout 
that sends and receives messages from the LRUs'''
import time
from abc import ABC, abstractmethod
import zmq


from config.config import DISCONNECTED, DONE
from config.config import FIELD_STATUS

CLIENT_ENDPOINT = "tcp://*:5555"

class ZmqServer(ABC):
    '''Base class for the workout that sends and receives messages from the LRUs'''
    status = DISCONNECTED

    def __init__(self):

        context = zmq.Context()
        self.server = context.socket(zmq.REP)
        self.server.bind(CLIENT_ENDPOINT)

    @abstractmethod
    def check_status(self):
        '''check the status of the LRUs'''

    @abstractmethod
    def handle_message(self, message):
        '''handle the message from the client'''
    
    def run(self):
        '''start the zmq server'''
        while self.status < DONE:
            #receive a message and handle it
            message = self.server.recv_json()
            self.handle_message(message)

            #check the status of the LRUs
            self.check_status()

            #send heartbeat
            self.server.send_json({FIELD_STATUS: self.status})
            
            #take a nap
            time.sleep(0.5)

            #do it all again
            # print("zmq server running")