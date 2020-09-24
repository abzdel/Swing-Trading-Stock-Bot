import btalib, config, requests, json, time, ta
import pandas as pd
from datetime import datetime, timedelta, date
import warnings
from pandas.core.common import SettingWithCopyWarning
import alpaca_trade_api as tradeapi

##################################################-GET LIST OF SYMBOLS-##################################################
holdings=open('data/holdings.csv').readlines() # read csv of QQQ holdings - should be able to use any csv
#holdings=open('data/WILSHIRE-5000-Stock-Tickers-List.csv').readlines() # read csv of Wilshire 5000 - not using right now as I can only pass in 200 symbols

# pull symbols from holdings csv, assigns it to symbols variable (list of symbols)
symbols = [holding.split(',')[2].strip() for holding in holdings][1:] # use this line for QQQ holdings
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


##################################################-CALCULATE PIVOT POINT AND RESISTANCE LEVEL-##################################################
# df['pivot_point'] = (df['high'].shift(1) + df['low'].shift(1) + df['close'].shift(1))/3
# df['r1'] = (2*df['pivot_point']) - df['low'].shift(1)
# df['s1'] = (2*df['pivot_point']) - df['high'].shift(1)
# df['r2'] = (df['pivot_point'] - df['s1']) + (df['r1'])


df['pivot_point'] = (df['high'] + df['low'] + df['close'])/3
df['r1'] = (2*df['pivot_point']) - df['low']
df['s1'] = (2*df['pivot_point']) - df['high']
df['r2'] = (df['pivot_point'] - df['s1']) + (df['r1'])
df['take_profit'] = ((df['r2'] - df['close'])*.75) + df['close']
# for now, we will just trade on these levels
# if more are needed, they can be found and explained here:
# https://www.daytrading.com/pivot-points#:~:text=Calculation%20of%20Pivot%20Points,-Pivots%20points%20can&text=The%20central%20price%20level%20%E2%80%93%20the,or%20period%2C%20more%20generally).&text=Resistance%201%20%3D%20(2%20x%20Pivot,)%20%E2%80%93%20High%20(previous%20period)


##################################################-ADDING IN TIME-##################################################
# add in time - make sure the bot is not trying to trade based on the price of non-trading days
today = date.today()

# conditions to use last trading days as variables
if today.weekday() == 6: # sunday
    yesterday = today - timedelta(days=2)
    yesterday = yesterday.strftime('%Y-%m-%d')

    two_days_ago = today - timedelta(days=3)
    two_days_ago = two_days_ago.strftime('%Y-%m-%d')

    three_days_ago = today - timedelta(days=4)
    three_days_ago = three_days_ago.strftime('%Y-%m-%d')

    four_days_ago = today - timedelta(days=5)
    four_days_ago = four_days_ago.strftime('%Y-%m-%d')

if today.weekday() == 0: # monday
    yesterday = today - timedelta(days=3)
    yesterday = yesterday.strftime('%Y-%m-%d')

    two_days_ago = today -timedelta(days=4)
    two_days_ago = two_days_ago.strftime('%Y-%m-%d')

    three_days_ago = today - timedelta(days=5)
    three_days_ago = three_days_ago.strftime('%Y-%m-%d')

    four_days_ago = today - timedelta(days=6)
    four_days_ago = four_days_ago.strftime('%Y-%m-%d')

if today.weekday() == 1: # tuesday
    yesterday = today - timedelta(days=1)
    yesterday = yesterday.strftime('%Y-%m-%d')

    two_days_ago = today - timedelta(days=4)
    two_days_ago = two_days_ago.strftime('%Y-%m-%d')

    three_days_ago = today - timedelta(days=5)
    three_days_ago = three_days_ago.strftime('%Y-%m-%d')

    four_days_ago = today - timedelta(days=6)
    four_days_ago = four_days_ago.strftime('%Y-%m-%d')

if today.weekday() == 2: # wednesday
    yesterday = today - timedelta(days=1)
    yesterday = yesterday.strftime('%Y-%m-%d')

    two_days_ago = today - timedelta(days=2)
    two_days_ago = two_days_ago.strftime('%Y-%m-%d')

    three_days_ago = today - timedelta(days=5)
    three_days_ago = three_days_ago.strftime('%Y-%m-%d')

    four_days_ago = today - timedelta(days=6)
    four_days_ago = four_days_ago.strftime('%Y-%m-%d')

if today.weekday() == 3: # thursday
    yesterday = today - timedelta(days=1)
    yesterday = yesterday.strftime('%Y-%m-%d')

    two_days_ago = today - timedelta(days=2)
    two_days_ago = two_days_ago.strftime('%Y-%m-%d')

    three_days_ago = today - timedelta(days=3)
    three_days_ago = three_days_ago.strftime('%Y-%m-%d')

    four_days_ago = today - timedelta(days=6)
    four_days_ago = four_days_ago.strftime('%Y-%m-%d')

if today.weekday() == 4 or today.weekday() == 5: # friday or saturday
    yesterday = today - timedelta(days=1)
    yesterday = yesterday.strftime('%Y-%m-%d')

    two_days_ago = today - timedelta(days=2)
    two_days_ago = two_days_ago.strftime('%Y-%m-%d')

    three_days_ago = today - timedelta(days=3)
    three_days_ago = three_days_ago.strftime('%Y-%m-%d')

    four_days_ago = today - timedelta(days=4)
    four_days_ago = four_days_ago.strftime('%Y-%m-%d')

today = today.strftime('%Y-%m-%d')


##################################################-FILTER DATA-##################################################
# first, let's only work with the last three days of data
big_money_df = df.loc[(df['time']==today) |
                      (df['time']==yesterday) |
                      (df['time']==two_days_ago) |
                      (df['time']==three_days_ago)] # only take records from up to three days ago


warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)
# warning being ignored - despite the error, I am still getting the expected result
big_money_df.loc[:, 'above_sma10'] = (big_money_df['close'] > big_money_df['sma10']) # a simple column to detect if a stock is above or below the SMA 10-day line
# setwithcopy warning - uncomment the following to ensure the code worked correctly
# print((big_money_df['close'] > big_money_df['sma5']).sum())
# print(big_money_df['above_sma5'].value_counts())
# first value should match the true values

buy_stocks = big_money_df.loc[

                            ##########-RSI LESS THAN 70-##########
                            (big_money_df['rsi'] < 70)


                            ##########-CHECK IF SMA LINE HAS BEEN CROSSED-##########
                            # three days ago, the price action was below the SMA line
                            # two days ago and yesterday, the price action was above the SMA line
                            # we want to know if the price action has held above the SMA line for two days in a row after being below it
                            & (big_money_df['above_sma10'].shift(3) == False) # below SMA 3 days ago
                            & (big_money_df['above_sma10'].shift(2) == True) # above SMA 2 days ago
                            & (big_money_df['above_sma10'].shift(1) == True) # above SMA yesterday
                            & (big_money_df['above_sma10'] == True) # above SMA today
                            & (big_money_df['close'].shift(1) > big_money_df['sma200'])


                            ##########-CHECK IF SHORT TERM SMA > LONG TERM SMA FOR THREE DAYS-##########
                            & (big_money_df['sma10'] > big_money_df['sma200']) # today
                            & (big_money_df['sma10'].shift(1) > big_money_df['sma200'].shift(1)) # yesterday
                            & (big_money_df['sma10'].shift(2) > big_money_df['sma200'].shift(2)) # two days ago


                            ##########-ONLY RETURN RECORDS FROM TODAY-##########
                            & (big_money_df['time']==today)

                                ]


buy_stocks = buy_stocks.sort_values(by=['rsi']) # sort values by RSI

# print('these are the best stocks to buy, if available:')
#print(buy_stocks[['symbol', 'close', 'sma10', 'sma200', 'r2', 'rsi']])


"""
The following takes into account the current price of each stock in our buy list. This slows down the bot tremendously and, since I don't
want to day trade, having the exact current price at any given time is not super important. I will leave the code here in case I decide to use it once
again.

##################################################-REMOVE IF CURRENT PRICE < SMA10 -##################################################
# construct that should avoid daytrades - may no longer be needed with sma10 if it works well enough (was meant to help sma5 issue)
api = tradeapi.REST(config.APCA_API_KEY_ID, config.APCA_API_SECRET_KEY, config.APCA_API_BASE_URL) # set URLs

# WILL NOT WORK IF NON-TRADING DAY
price_list = []
for stock in stocks_to_buy:
    barset = api.get_barset(stock, '1Min', limit=1)
    stock_price = barset[stock][0].c #get current price
    price_list.append(stock_price)
buy_stocks['current_price'] = price_list

buy_stocks = buy_stocks[buy_stocks['time']==today]
buy_stocks = buy_stocks[buy_stocks.current_price >= buy_stocks.sma5]
# print(buy_stocks[['symbol', 'close', 'sma5', 'above_sma5', 'sma200']])

buy_stocks = buy_stocks.loc[(buy_stocks['current_price'] > buy_stocks['sma10'])]
buy_stocks = buy_stocks.sort_values(by=['rsi'])
#print(buy_stocks[['symbol', 'sma10', 'current_price', 'rsi']])

# PROBLEM - sma5 was super reactive - EA constantly fluctuated between a buy and a sell, which triggered
# lots of day trades. Going to try the bot with SMA10 for a while

"""
