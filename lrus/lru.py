'''Base class for LRUs with mongo, and other info'''
from abc import ABC, abstractmethod
from mongo import Mongo

STOPPED = -1
CONNECTED = 0
PAUSED = 1
UNPAUSE = 2
RUNNING = 3
DONE = 4


class LRU(ABC):
    def __init__(self):
        self.mongo = Mongo()

    def to_time(self, secs):
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
 

        pass