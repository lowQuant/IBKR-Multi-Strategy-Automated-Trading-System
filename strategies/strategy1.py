import time
from shared_resources import ib, add_log, start_event

PARAMS = {
    1:{'name':'Monthly Trendfilter','value': 10,
       'description':"The 10M SMA Trendfilter is used as a sell signal if the price drops below."},
    2:{'name':"Structural Trendfilter",'value':50,
       'description':"""This filter is used to re-enter the market if the price is below the monthly trendfilter
                        and was below the structural trend, but price just crossed this structural trendline from below."""},
    3:{'name':'Equity Weight','value':30,'description':'Weight for equity allocation'},
    4:{'name':'Fixed Income Weight','value':90,'description':'Weight for FI allocation'},
}

def strategy1():
    add_log("Strategy1 Thread Started")
    start_event.wait()
    add_log("Executing Strategy 1")
    while True:
        time.sleep(10)
        add_log("S1: Placing a Buy Order in MSFT")
