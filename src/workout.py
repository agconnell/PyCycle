import os
import atexit
import subprocess
from pathlib import Path
import time
from datetime import datetime as dt
import uuid
from math import floor, ceil
from db.mongo import Mongo

DONE = 'done'
PAUSE = 'pause'
XAXIS_RANGE = 60*5 #5 minutes
TICK_GAP = 30 #30 seconds

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

    def ticker(self, min, max):
        ticks = []
        max = max + TICK_GAP    
        if max <= 300:
            min = 0
            max = 330
        for i in range(min, max, TICK_GAP):
            ticks.append(i)
        return ticks

    def get_hr_data(self):
        data = self.collection.find({'id': self.uuid}).sort('timestamp', 1)
        data = list(data.limit(XAXIS_RANGE))
        if len(data) == 0:
            return [], [], []
        
        res = {key: [d[key] for d in data] for key in data[0].keys()}
        yvals = res['bpm']
        xvals = res['timestamp']

        min = xvals[0]
        max = xvals[-1]
        ticks = self.ticker(min, max)


        return xvals, yvals, ticks
    
    def start(self):
        print('Start main')
        if Path(DONE).exists():
            os.remove(DONE)
        if Path(PAUSE).exists():
            os.remove(PAUSE)
        
        subprocess.Popen(["python", "hrm/hrm.py", self.uuid])
            
    def stop(self):
        print('Shutdown')
        Path(DONE).touch()
        time.sleep(2)

    def pause(self):
        print('Pause')
        Path(PAUSE).touch()
        time.sleep(2)

    def msg_callback(self, msg):
        print(msg)  
