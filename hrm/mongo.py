'''write workout data to a mongo database'''

from pymongo import MongoClient

class Mongo():
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['workouts']
        self.collection = self.db['workout_data']

    def insert_data_point(self, d):
        self.collection.insert_one(d)
        # print(f'{signal}: {value}')

    def close(self):
        self.client.close()