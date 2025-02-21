import sys
import atexit
import subprocess
import uuid
from math import floor, ceil
from db.mongo import Mongo
from pymongo import DESCENDING, ASCENDING
import zmq
import threading
import time
import json


STOPPED = 0
PAUSED = 1
UNPAUSE = 2
RUNNING = 3
DONE = 4

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
    def __init__(self, cb_hr, cb_power, cb_cadence):
        atexit.register(self.stop)   
        self.mongo = Mongo()
        self.collection = self.mongo.get_collection()
        self.uuid = uuid.uuid4().hex
        self.status = STOPPED

        self.msg_thread = threading.Thread(target=self.msg_workers)
        self.msg_thread.start()

        self.cb_hr = cb_hr
        self.cb_power = cb_power
        self.cb_cadence = cb_cadence

        #keeps track of which lrus are connected
        self.connections_state = {'bpm': 0, 'Watts': 0, 'rpm': 0}

    def __del__(self):
        self.status =  DONE
        time.sleep(1)
        print(f"Object {self.name} destroyed.")

    def set_vals(self, k, v):
        if k == 'bpm':
            self.cb_hr(v)
        elif k == 'Watts':
            self.cb_power(v)
        elif k == 'rpm':
            self.cb_cadence(v)

    def get_connection_status(self):
        # if self.connections_state['bpm'] == True and self.connections_state['Watts'] == True and  self.connections_state['rpm'] == True:
        #     self.
        return self.connections_state

    def msg_workers(self):
        context = zmq.Context()
        server = context.socket(zmq.REP)
        server.bind("tcp://*:5555")

        while self.status < DONE:
            s = str(self.status).encode()
            try:
                data = json.loads(server.recv_json())

                print(f'workout recieved state: {data}')
                if "connected" in data:
                    f = data['field']
                    c = data['connected']
                    self.connections_state[f] = c
                    print(f"{f} connection state {c}")
                elif 'field' in data and 'value' in data:
                    self.set_vals(data['field'], data['value'])
                server.send(s)
                print(f'workout sending state: {self.status}')
            except Exception as e:
                print(f'zmq receiver not ready: {e}')

            time.sleep(0.5)

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
        self.set_status(RUNNING)
        python_executable = sys.executable
        subprocess.Popen([python_executable, 'lrus/data_generator.py', 'bpm', self.uuid])
        subprocess.Popen([python_executable, 'lrus/data_generator.py', 'Watts', self.uuid])
        subprocess.Popen([python_executable, 'lrus/data_generator.py', 'rpm', self.uuid])
      
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

