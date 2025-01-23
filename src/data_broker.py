
class Data():
    def __init__(self):
        self.timestamp = None
        self.run_time = 0
        self.value = 0

class DataBroker:
    def __init__(self):
        self.observers = {}

    def add_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def add_data(self, data):        
        for observer in self.observers:
            observer.notify(data)