from collections import deque
import threading, time, os, configparser
from ib_insync import *


log_buffer = deque(maxlen=5)
log_lock = threading.Lock()
start_event = threading.Event()

def add_log(message):
    with log_lock:
        log_buffer.append(f"{time.ctime()}: {message}")

ib = IB()
try:
    settings_file = 'settings.ini'
    settings = configparser.ConfigParser()
    settings.read(settings_file)
    if 'DEFAULT' in settings:
        port = int(settings['DEFAULT'].get('port',7497))
    ib.connect('127.0.0.1', port, clientId=0) 
except:
    try:
        ib.connect('127.0.0.1', 7497, clientId=0) 
    except:
        add_log('IBKR connection failed.')