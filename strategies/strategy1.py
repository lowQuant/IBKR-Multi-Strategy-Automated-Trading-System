import time
import pandas as pd
import datetime as dt
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

class Strategy:
    def __init__(self,ib):
        self.running = True  # This flag controls the while loop in the run method
        self.universe = {1:{'symbol':"IUSQ",'weight':0.3},
                         2:{'symbol':"SYB3",'weight':0.35},
                         3:{'symbol':"IBTE",'weight':0.35}}                   
        try:
            # Load Cash Value from Supabase databank 
            self.cash = 1/0
        except:
            # Get Cash Value from settings.ini weight * total portfolio cash
            weight = 0.3
            total_cash = float([line for line in ib.accountSummary() if line.tag == 'TotalCashValue'][0].value)
            self.cash = total_cash * weight

    def warm_up(self, contract):
        '''Downloading historical data for each asset in the universe'''

        def last_day_of_month(any_day):
            # The day 28 exists in every month. 4 days later, it's always next month
            next_month = any_day.replace(day=28) + dt.timedelta(days=4)
            # subtracting the number of the current day brings us back one month
            return (next_month - dt.timedelta(days=next_month.day)).day

        df = util.df(ib.reqHistoricalData(contract,endDateTime='',durationStr='5 Y',barSizeSetting='1 day',whatToShow='TRADES',useRTH=True,formatDate=1))
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        # Add a column that identifies the last trading day of the month
        df['last_day_of_month'] = df.index.map(last_day_of_month)
    


    def buy_engine(self):
        # Placeholder buy/sell engines
        add_log("Selecting buy/sell engines...")

        for asset in self.universe:
            symbol = self.universe[asset]['symbol']
            contract = Stock(symbol, 'SMART', 'EUR')

            # is asset invested?
            if symbol in [position.contract.symbol for position in ib.positions()]:
                invested = True

                # is the asset weight below its allocation range (0.2 - 0.3?)

            dfd, dfm = self.warm_up(symbol)

    def select_portfolio(self):
        # Placeholder for portfolio selection
        add_log("Selecting portfolio...")

    def size_initial_position(self):
        # Placeholder for sizing initial position
        add_log("Sizing initial position...")

    def execute_initial_positions(self):
        # Placeholder for executing initial positions
        add_log("Executing initial positions...")

    def check_ongoing_position_size(self):
        # Check the size of ongoing positions
        add_log("Checking ongoing position size...")
        positions = ib.positions()
        for position in positions:
            # Log the position details; implement any size checking logic as required
            add_log(f"Position in {position.contract.symbol}: {position.position}")

    def execute_position_adjustments(self):
        # Placeholder for position adjustments
        add_log("Executing position adjustments...")

    def run(self):
        start_event.wait()  # Wait for the start event to be set
        
        self.select_buy_sell_engines()
        self.select_portfolio()
        self.size_initial_position()
        self.execute_initial_positions()
        while self.running:
            self.check_ongoing_position_size()
            self.execute_position_adjustments()
            time.sleep(10)  # Wait for 10 seconds before checking again

def strategy1(Strategy):
    strategy = Strategy()
    try:
        add_log("Strategy1 Thread Started")
        strategy.run()
    except KeyboardInterrupt:
        add_log("Strategy1 Thread Stopped")
        strategy.running = False  # Set running to False to stop the loop


