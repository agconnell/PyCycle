import os, sys
import atexit
import subprocess
from pathlib import Path
import time
from datetime import datetime as dt
import uuid
from math import floor, ceil
from db.mongo import Mongo
from pymongo import DESCENDING, ASCENDING
import zmq

STOPPED = 0
RUNNING = 1
PAUSED = 2
UNPAUSE = 4
DONE = 3


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
    
class Workout():
    def __init__(self):
        atexit.register(self.stop)   
        self.mongo = Mongo()
        self.collection = self.mongo.get_collection()
        self.uuid = uuid.uuid4().hex
        self.status = STOPPED

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind("tcp://*:5555")

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

        self.send_status()
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
    
    def start(self):
        print('Start main')
        self.status = RUNNING
        python_executable = sys.executable
        subprocess.Popen([python_executable, 'fake_data/data_generator.py', 'bpm', self.uuid])
        subprocess.Popen([python_executable, 'fake_data/data_generator.py', 'Watts', self.uuid])
        subprocess.Popen([python_executable, 'fake_data/data_generator.py', 'rpm', self.uuid])
            
    def stop(self):
        print('Stop')
        self.status = STOPPED

    def pause(self):  
        print('pause')     
        if self.status == PAUSED:
            self.status = UNPAUSE
            self.send_status()
            self.status = RUNNING
        else:
            self.status = PAUSED

    def is_paused(self):    
        return self.status == PAUSED
        
    def send_status(self):
        s = str(self.status)
        self.socket.send_string(s)

    def msg_callback(self, msg):
        print(msg)  
