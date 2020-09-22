import biz_bot_scrape as bb1
import pandas as pd
import numpy as np
import alpaca_trade_api as tradeapi
import config, websocket, json, re, requests
from urllib.error import HTTPError
import btalib, ta
from datetime import *

##################################################-SETUP-##################################################
api = tradeapi.REST(config.APCA_API_KEY_ID, config.APCA_API_SECRET_KEY, config.APCA_API_BASE_URL)
portfolio = api.list_positions() # get account info


##################################################-FIND CURRENT POSITIONS-##################################################
# create empty list for current holdings and quantity held
current_holdings_df = pd.DataFrame()
current_holdings = []
holding_qty = []
equity_owned = []
current_price = []

# regular expression to pull symbol, quantity, market value, and current price out of portfolio object
i=0 # used for indexing each item in our portfolio - will increase with each iteration of the loop
for stock in portfolio:
    temp = re.search(r"(('symbol': '))+((\w+))",str(portfolio[i])).group(3)
    current_holdings.append(temp)
    temp2 = re.search(r"(('qty': '))+((\w+))",str(portfolio[i])).group(3)
    holding_qty.append(temp2)
    temp3 = re.search(r"(('market_value': '))+((\w+))",str(portfolio[i])).group(3)
    equity_owned.append(temp3)
    temp4 = re.search(r"(('current_price': '))+((\w+))",str(portfolio[i])).group(3)
    current_price.append(temp4)
    i+=1

# append each list to our dataframe
current_holdings_df['symbol'] = current_holdings

holding_qty = [float(i) for i in holding_qty]
current_holdings_df['qty_owned'] = holding_qty

equity_owned = [float(i) for i in equity_owned]
current_holdings_df['equity_owned'] = equity_owned

current_price = [float(i) for i in current_price]
current_holdings_df['current_price'] = current_price


##################################################-SCRAPE DATA FOR CURRENT HOLDINGS-##################################################
symbols = current_holdings

symbols = [symbol.split(',')[0].strip() for symbol in symbols] # use this line for QQQ holdings
#symbols = [holding.split(',')[0].strip() for holding in holdings][1:] # use this line for Wilshire 5000
symbols = ",".join(symbols)

day_bars_url = '{}/day?symbols={}&limit=201'.format(config.BARS_URL, symbols) #get daily data every day for 200 days (for each symbol)
r=requests.get(day_bars_url, headers=config.HEADERS) # use requests module to search each URL
data = r.json() # gives us the data in a dictionary


##################################################-SET UP DATA CONTAINERS-##################################################
df = pd.DataFrame() # create empty dataframe
# create empty lists for each piece of data we're scraping
time_list = []
open_list = []
high_list = []
low_list = []
close_list = []
volume_list = []
symbol_list = []


##################################################-SCRAPE DATA-##################################################
for symbol in data:
    for bar in data[symbol]:
        t = datetime.fromtimestamp(bar['t']) # change from UNIX timestamp to datetime object
        day = t.strftime('%Y-%m-%d') # save to day variable
        # append each variable to its own list, will add to df later
        time_list.append(day)
        open_list.append(bar['o'])
        high_list.append(bar['h'])
        low_list.append(bar['l'])
        close_list.append(bar['c'])
        volume_list.append(bar['v'])
        symbol_list.append(symbol)
# append each list to its own column in df
df['symbol'] = symbol_list
df['time'] = time_list
df['open'] = open_list
df['high'] = high_list
df['low'] = low_list
df['close'] = close_list
df['volume'] = volume_list


##################################################-ADDING IN INDICATORS-##################################################
sma2 = btalib.sma(df, period=2)
df['sma2']=sma2.df
sma5 = btalib.sma(df, period=5)
df['sma5']=sma5.df
sma10 = btalib.sma(df, period=10)
df['sma10']=sma10.df
sma20 = btalib.sma(df, period=20)
df['sma20']=sma20.df
sma200 = btalib.sma(df, period=200)
df['sma200']=sma200.df
df['rsi'] = ta.momentum.rsi(df.close, n=6, fillna=False) # btalib rsi not working, we will use talib for this indicator


##################################################-JOIN THE TWO DATAFRAMES-##################################################
today = str(date.today())
df = df.loc[df['time']==today] # we only want today's records

df = df.merge(current_holdings_df, on='symbol', how='outer')


##################################################-CALCULATE PIVOT POINT AND RESISTANCE LEVEL-##################################################
df['pivot_point'] = (df['high'].shift(1) + df['low'].shift(1) + df['close'].shift(1))/3
df['r1'] = (2*df['pivot_point']) - df['low'].shift(1)
df['s1'] = (2*df['pivot_point']) - df['high'].shift(1)
df['r2'] = (df['pivot_point'] - df['s1']) + (df['r1'])


##################################################-CRITERIA FOR SELLING-##################################################
sell_df = df.loc[


                        ##########-(RSI > 70)-##########
                        (df['rsi'] > 70)

                        ##########-CLOSE HOLDS BELOW SMA LINE-##########
                    |   ((df['close'].shift(1) < df['sma10'].shift(1)) & (df['close'] < df['sma10'])

                        ##########-CURRENT PRICE OR CLOSE REACHES 75% OF RESISTANCE LEVEL 2-##########
                    |   (((df['current_price']) >= (.75*df['r2'])) | ((df['close']) >= (.75*df['r2'])))

                        ##########-CLOSE DIPS BELOW LONG-TERM SMA-##########
                    |   (df['close'] < df['sma200']))

                    # future idea - keep stock if the RSI is under 30 - will see how the current system works first

                    ]


##################################################-SELL STOCKS-##################################################
if sell_df.empty == False: # if there are stocks to sell
    portfolio = api.list_positions()
    print(f"stocks being sold: {list(sell_df['symbol'])}")
    i=0 # used for indexing
    for stock in sell_df['symbol']:
        try:
            api.submit_order(
                symbol=sell_df['symbol'].iloc[i],
                qty=sell_df['qty_owned'].iloc[i],
                side='sell',
                type='market',
                time_in_force='gtc')
            print(f'{stock} sold')
            i+=1
        except (requests.exceptions.HTTPError, tradeapi.rest.APIError):
            print(f"Either your order to sell {stock} hasn't been filled, or daytrade protection has been activated")
            continue
