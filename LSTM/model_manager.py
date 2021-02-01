#!/usr/bin/env python3

import atexit
from multiprocessing import Lock
from multiprocessing.managers import BaseManager
import model


lock = Lock()
model = model.Model("./weights")

def get_connection():
    global model
    with lock:
        return model


@atexit.register
def close_connections():
    pass

manager = BaseManager(('', 37844), b'password')
manager.register('get_connection', get_connection)
server = manager.get_server()
server.serve_forever()

for i in range(10):
    print(model)
