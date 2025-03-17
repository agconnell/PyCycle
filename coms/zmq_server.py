'''
This module contains the ZMQ_Server class that is the base class for the workout 
that sends and receives messages from the LRUs'''
import time
from abc import ABC, abstractmethod
import zmq
import logging


from config.config import DISCONNECTED, DONE, SOCKET_TIMEOUT
from config.config import FIELD_STATUS

CLIENT_ENDPOINT = "tcp://*:5555"
SLEEP_INTERVAL = 1

class ZmqServer(ABC):
    '''Base class for the workout that sends and receives messages from the LRUs'''
    status = DISCONNECTED

    def __init__(self):

        context = zmq.Context()
        self.socket = context.socket(zmq.REP)
        self.socket.bind(CLIENT_ENDPOINT)

    @abstractmethod
    def check_lru_status(self):
        '''check the status of the LRUs'''

    @abstractmethod
    def handle_message(self, message):
        '''handle the message from the client'''
    
    def run(self):
        '''start the zmq server'''
        logging.debug("Start ZMQ server")
        poller = zmq.Poller()
        poller.register(self.socket, zmq.POLLIN)
        socks = dict(poller.poll(SOCKET_TIMEOUT))
        while self.status < DONE:
            try:
                #receive a message and handle it
                if self.socket in socks and socks[self.socket] == zmq.POLLIN:
                    message = self.socket.recv_json()
                    self.handle_message(message)
                    logging.debug("ZMQ server received message: %s", message)

                    
                    #send heartbeat
                    logging.debug("ZMQ server sending status hearrbeat: %s", self.status)
                    self.socket.send_json({FIELD_STATUS: self.status})
                    time.sleep(SLEEP_INTERVAL)
                else:
                    logging.warning("Socket timed out connecting to device")
                    raise zmq.ZMQError("Socket timed out connecting to device(s).  Make sure they are on")
                
            except zmq.ZMQError as e:
                logging.error("ZMQ error in ZMQ server: %s", e)
                break
            except ValueError as e:
                logging.error("Value error in ZMQ server: %s", e)
                break
            except Exception as e:
                logging.error("Unexpected error in ZMQ server: %s", e)
                break

