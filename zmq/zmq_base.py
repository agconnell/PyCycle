

#ZMQ vars
REQUEST_TIMEOUT = 5000
REQUEST_RETRIES = 3
SERVER_ENDPOINT = "tcp://localhost:5555"
CLIENT_ENDPOINT = "tcp://*:5555"

# Application States
DISCONNECTED = 0
CONNECTED = 1
STOPPED = 2
RUNNING = 3
PAUSED = 4
DONE = 5

# connection signals
CONNECT = 1
KEEP_ALIVE = 2

# seconds before a lru is disconnected
TIMEOUT = 5

# message properties
FIELD_ID = 'id'
FIELD_NAME = 'field'
FIELD_VALUE = 'value'
FIELD_STATUS = 'status'
FIELD_LAST_UPDATE = 'last_update'