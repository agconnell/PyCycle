
import time
import threading

from zmq_server import ZMQ_Server
from zmq_client import ZMQ_Client
from zmq_base import *

from zmq_base import DISCONNECTED, CONNECTED, STOPPED, RUNNING, PAUSED, DONE
from zmq_base import FIELD_NAME, FIELD_VALUE, FIELD_STATUS

if __name__ == "__main__":
    lrus_ids = ['client1','client2']
    server = ZMQ_Server(lrus_ids)
    st = threading.Thread(target=server.run)
    st.start()
            
    client1 = ZMQ_Client("client1", 'field 1')
    ct1 = threading.Thread(target=client1.run)
    ct1.start()
            
    client2 = ZMQ_Client("client2", 'field 2')
    ct2 = threading.Thread(target=client2.run)
    ct2.start()