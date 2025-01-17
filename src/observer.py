from data_broker import DataBroker, Data
import abc

class Observer:
    def __init__(self):
        self.values = []

    def register(self, data_broker: DataBroker):
        data_broker.add_observer(self)

    def unregister(self, data_broker: DataBroker):
        data_broker.remove_observer(self)

    @abc.abstractmethod
    def notify(self, data: Data, **kwargs):
        '''abstract method art'''