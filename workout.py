
'''Workout class that handles the workout data from the LRUs'''
import sys
import atexit
import subprocess
import uuid
import threading
import time
import logging
from datetime import datetime
from statistics import mean


from zmq_server import ZmqServer
from config import DISCONNECTED, CONNECTED, STOPPED, RUNNING, DONE
from config import FIELD_NAME, FIELD_VALUE, REQUEST_TIMEOUT, MAX_POINTS


class Workout(ZmqServer):
    '''Workout class that handles the workout data from the LRUs'''

    def __init__(self, cb_hr, cb_power, cb_cadence):
        super().__init__()

        atexit.register(self.done)

        self.uuid = uuid.uuid4().hex
        self.status = STOPPED

        self.cb_hr = cb_hr
        self.cb_power = cb_power
        self.cb_cadence = cb_cadence

        #keeps track of which lrus are connected
        #TODO: this needs to be moved to config page
        self.values = {'bpm': [(0, 0, 0)], 'Watts': [(0, 0, 0)], 'rpm': [(0, 0, 0)]}
        self.last_updates = {'bpm': 0, 'Watts': 0, 'rpm': 0}
        self.connection_states = {'bpm': DISCONNECTED, 'Watts': DISCONNECTED, 'rpm': DISCONNECTED}
        self.status = DISCONNECTED
        self.t = 0

    def __del__(self):
        self.status =  DONE
        time.sleep(1)
   
    # def check_lru_status(self):
    #     cur_time = datetime.now().timestamp()
    #     status = self.status
    #     if cur_time - last_update > REQUEST_TIMEOUT:
    #         self.connection_states[lru] = DISCONNECTED
    #         status = DISCONNECTED
    #         logging.info('LRU: %s is disconnected - last update: %s', lru, cur_time - last_update)

    #     if status == DISCONNECTED:
    #         self.status = DISCONNECTED

    def get_last_value(self, lru) -> int :
        '''returns the latest value  
        '''
        if lru in self.values and len(self.values[lru]) > 0:
            #TODO make the tuple a numed tuple so this is clearer
            return self.values[lru][-1][0]
        else:
            logging.warning('No value for: %s', lru)
            return 0
        
    def get_last_point(self, lru) -> int :
        '''returns the latest value  
        '''
        if lru in self.values and len(self.values[lru]) > 0:
            #TODO make the tuple a numed tuple so this is clearer
            return self.values[lru][-1][1], self.values[lru][-1][0]
        else:
            logging.warning('No value for: %s', lru)
            return 0

    def to_time(self, secs):
        '''converts seconds into a time format for display 
            like 90 seconds --> 1:30'''
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

    def set_vals(self, field_name, value, time_stamp ):
        '''update with the latest value'''

        if self.status == RUNNING:
            # only update the run time while the workout is running
            self.t += 1

            self.values[field_name].append((value, self.t, time_stamp))
            # TODO: it seems like you could do a slice, but that is failing when < 100
            # items, so doing with loop, will check for better way
            while len(self.values[field_name]) > MAX_POINTS:
                self.values[field_name].pop(0)
        if self.status == STOPPED or self.status == CONNECTED:
            self.values[field_name][0] = (value, self.t, time_stamp)

    def handle_message(self, message):
        '''receives a message from a LRU and updates the list of values for that LRU'''
        cur_time = datetime.now().timestamp()
        lru = message[FIELD_NAME]
        value = message[FIELD_VALUE]
        if lru in self.last_updates:
            self.last_updates[lru] = cur_time - self.last_updates[lru]
            self.set_vals(lru, value, cur_time)
            self.connection_states[lru] = CONNECTED
            if self.status == DISCONNECTED:
                self.status = CONNECTED
            logging.info('Workout received update: %s',  message)
        else:
            logging.info('Workout received update from unknown lru:  %s',  message)

    def get_lru_status(self, field_name):
        '''Returns the status of the names LRU'''
        return self.connection_states[field_name]

    def get_status(self):
        '''Returns the status of the running workout
        TODO: this should be the sum of the statuses of the running LRUs'''
        return self.status

    def connect(self):
        '''Connects the LRUs
        TODO: the LRUs should be configurable not hard coded'''
        print('Connect')
        self.status = DISCONNECTED


        python_executable = sys.executable
        subprocess.Popen([python_executable, 'hrm.py', 'bpm'])
        # subprocess.Popen([python_executable, 'lrus/data_generator.py', 'bpm'])
        # subprocess.Popen([python_executable, 'lrus/data_generator.py', 'Watts'])
        # subprocess.Popen([python_executable, 'lrus/data_generator.py', 'rpm'])
      
        server_thread = threading.Thread(target=self.run)
        server_thread.start()

    def start(self):
        '''Starts/stops the workout'''
        if self.status == RUNNING:
            print('Stop')
            self.status = STOPPED
        else:
            print('Start')
            self.status = RUNNING

    def done(self):
        '''Ends the workout'''
        print('DONE!')
        self.status = DONE

