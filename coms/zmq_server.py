'''
This module contains the ZMQ_Server class that is the base class for the workout 
that sends and receives messages from the LRUs'''
import time
from abc import ABC, abstractmethod
import zmq
import logging


from config.config import DISCONNECTED, DONE
from config.config import FIELD_STATUS

CLIENT_ENDPOINT = "tcp://*:5555"
SLEEP_INTERVAL = 0.5

class ZmqServer(ABC):
    '''Base class for the workout that sends and receives messages from the LRUs'''
    status = DISCONNECTED

    def __init__(self):

        context = zmq.Context()
        self.server = context.socket(zmq.REP)
        self.server.bind(CLIENT_ENDPOINT)

    @abstractmethod
    def check_lru_status(self):
        '''check the status of the LRUs'''

    @abstractmethod
    def handle_message(self, message):
        '''handle the message from the client'''
    
    def run(self):
        '''start the zmq server'''
        while self.status < DONE:
            try:
                #receive a message and handle it
                message = self.server.recv_json()
                self.handle_message(message)

                #check the status of the LRUs
                self.check_lru_status()

                #send heartbeat
                self.server.send_json({FIELD_STATUS: self.status})
                
                #take a nap
                time.sleep(SLEEP_INTERVAL)
            except zmq.ZMQError as e:
                logging.error("ZMQ error in ZMQ server: %s", e)
                break
            except ValueError as e:
                logging.error("Value error in ZMQ server: %s", e)
                break
            except Exception as e:
                logging.error("Unexpected error in ZMQ server: %s", e)
                break
            time.sleep(SLEEP_INTERVAL)
