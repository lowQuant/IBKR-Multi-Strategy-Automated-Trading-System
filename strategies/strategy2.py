import time
from shared_resources import add_log, start_event

def strategy2():
    add_log("Strategy2 Thread Started")
    start_event.wait()
    add_log("Executing Strategy 2")
    while True:
        time.sleep(9)
        add_log("S2: Placing a Buy Order in AAPL")

    