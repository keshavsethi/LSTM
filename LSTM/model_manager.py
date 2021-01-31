#!/usr/bin/env python3

import atexit
from multiprocessing import Lock
from multiprocessing.managers import BaseManager
import model

model = model.Model("./weights")
lock = Lock()


def get_connection():
    with lock:
        return model


@atexit.register
def close_connections():
    model.reset()

manager = BaseManager(('', 37844), b'password')
manager.register('get_connection', get_connection)
server = manager.get_server()
server.serve_forever()

## flast function

