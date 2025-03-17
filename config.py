


# Application States
DISCONNECTED = 0
CONNECTED = 1
STOPPED = 2
RUNNING = 3
DONE = 4
FAILED = -1

# seconds before a lru is disconnected
REQUEST_TIMEOUT = 5000
SOCKET_TIMEOUT = 20000
REQUEST_RETRIES = 3
SLEEP_TIME = 0.5
SERVER_ENDPOINT = "tcp://localhost:5555"

XAXIS_RANGE = 30 #5 minutes
TICK_GAP = 5 #30 seconds
MAX_POINTS = 100 #max number of points to keep in the plot
    
# message properties
FIELD_ID = 'id'
FIELD_LRU = 'lru'
FIELD_NAME = 'field'
FIELD_VALUE = 'value'
FIELD_TIME = 'tick'
FIELD_LRU_STATUS = 'lru_status'
FIELD_APP_STATUS = 'app_status'
FIELD_LAST_UPDATE = 'last_update'
