'''write workout data to a mongo database'''

from pymongo import MongoClient
from datetime import datetime as dt

class Mongo():
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['workouts']
        self.collection = self.db['workout_data']

    def insert_data_point(self, signal, value):
        n = dt.now()
        d = {'date': n, 'timestamp': n.timestamp(), signal: value}
        self.collection.insert_one(d)
        print(f'{signal}: {value}')

    def get_collection(self):
        return self.collection

    def close(self):
        self.client.close()