'''write workout data to a mongo database'''

from pymongo import MongoClient, InsertOne
from datetime import datetime as dt

class Mongo():
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['workouts']
        self.collection = self.db['workout_data']

    def insert_hr_data_point(self, data):
        d = {'date': dt.now(), 'hr': data.bpm}
        # self.collection.insert_one(d)
        print(f'hr: {data.bpm}')
   
    def insert_power_data_point(self, data):
        d = {'date': dt.now(), 'instantaneous_power': data.instantaneous_power, 'pedal_power_balance': data.pedal_power_balance}
        self.collection.insert_one(d)
        print(f'instantaneous_power: {data.instantaneous_power}')

    def close(self):
        self.client.close()