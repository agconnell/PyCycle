import sys
import atexit
import subprocess
import uuid
from math import floor, ceil
from pymongo import ASCENDING
from datetime import datetime
import threading
import time
import json
import logging

from db.mongo import Mongo
from coms.zmq_server import ZMQ_Server
from config.config import STOPPED, CONNECTED, RUNNING, DISCONNECTED, TIMEOUT


XAXIS_RANGE = 30 #5 minutes
TICK_GAP = 5 #30 seconds

##TODO move this to a common module it's duplicated in hrm.py
def to_time(secs):
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
    
class Workout(ZMQ_Server):

    def __init__(self, cb_hr, cb_power, cb_cadence):
        super().__init__(Workout.handle_message)
        
        atexit.register(self.stop)   
        self.mongo = Mongo()

        self.collection = self.mongo.get_collection()
        self.uuid = uuid.uuid4().hex
        self.status = STOPPED

        self.cb_hr = cb_hr
        self.cb_power = cb_power
        self.cb_cadence = cb_cadence

        #keeps track of which lrus are connected
        self.connections_state = {'bpm': 0, 'Watts': 0, 'rpm': 0}

    def __del__(self):
        self.status =  DONE
        time.sleep(1)
        print(f"Object {self.name} destroyed.")
   
    def check_status(self):
        print('workout check status does nothing')
        # cur_time = datetime.now().timestamp()
        # for lru, last_update in self.clients.items():
        #     if cur_time - last_update > TIMEOUT:
        #         lru.status = DISCONNECTED
        #         logging.warning(f'LRU: {lru.id} is disconnected - last update: {lru.last_update}')

    def handle_message(self, message):
        print(f'Server received: {message}')
        # if FIELD_ID in message and message[FIELD_ID] in self.lrus:
        #     self.lrus[message[FIELD_ID]].set_data(message)
        # else:
        #     logging.warning(f'Unknown LRU message: {message}')

    def set_vals(self, k, v):
        print('implement this')

    def get_connection_status(self):
        return self.connections_state

    def ticker(self, min, max, num_points):
        ticks = []
        max = max + TICK_GAP    
        if num_points < XAXIS_RANGE:
            min = 0
            max = XAXIS_RANGE + TICK_GAP
        for i in range(min, max, TICK_GAP):
            ticks.append(i)
        return ticks

    def get_data(self, field):
        data = self.collection.find({'id': self.uuid, field: { '$exists': True } }).sort('timestamp', ASCENDING)
        data = list(data)
        data = data[-XAXIS_RANGE:]
        
        if len(data) == 0:
            return [], [], []
        
        
        res = {key: [d[key] for d in data] for key in data[0].keys()}
        if field in res:
            yvals = res[field]
            xvals = res['timestamp']
        else:
            return [], [], []

        min = xvals[0]
        max = xvals[-1]
        ticks = self.ticker(min, max, len(xvals))

        return xvals, yvals, ticks
    
    def connect(self):
        print('Start main')
        self.set_status(DISCONNECTED)
        server_thread = threading.Thread(target=self.run)
        server_thread.start()
        python_executable = sys.executable

        subprocess.Popen([python_executable, 'lrus/data_generator.py', self.uuid, 'bpm'])
        # subprocess.Popen([python_executable, 'lrus/data_generator.py', self.uuid, 'Watts'])
        # subprocess.Popen([python_executable, 'lrus/data_generator.py', self.uuid, 'rpm'])
      
    def start(self):
        print('Start main')
        self.set_status(RUNNING)

    def stop(self):
        print('Stop')
        self.set_status(STOPPED)

    def done(self):
        print('DONE!')
        self.set_status(DONE)

    def pause(self):  
        print('pause')     
        if self.status == PAUSED:
            self.set_status(RUNNING)
        else:
            self.set_status(PAUSED)
        
    def set_status(self, status):
        self.status = status

