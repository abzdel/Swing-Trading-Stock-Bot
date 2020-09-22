import biz_bot_scrape as bb1
import pandas as pd
import alpaca_trade_api as tradeapi
import config, time, math

##################################################-SETUP-##################################################
api = tradeapi.REST(config.APCA_API_KEY_ID, config.APCA_API_SECRET_KEY, config.APCA_API_BASE_URL) # set URLs
account = api.get_account() # get account info
print('${} is available as buying power.'.format(account.buying_power)) # check buying power


##################################################-FINAL CRITERIA FOR BUYING-##################################################
current_holdings = [] # create empty list - will add stocks to it if bought - might not need if portfolio account variable in sell script updates fast enough

print('these are the best stocks to buy, if available:')
print(bb1.buy_stocks[['symbol', 'close', 'sma10', 'sma200', 'rsi']])
buy_stocks = bb1.buy_stocks['symbol'].tolist() # create a list of the stocks above
buy_stocks_list = [] # create empty list

for stock in buy_stocks:
    # we want to ensure we can afford each stock on our buy list
    # this loop filters out stocks we cannot afford by taking each element in buy_stocks, pulling its current price from the API, and adding it to our new list
    barset = api.get_barset(stock, '1Min', limit=1)
    stock_price = barset[stock][0].c #get current price of stock
    if stock_price < float(account.buying_power): # check if the stock's price is less than our buying power
        buy_stocks_list.append(stock)


##################################################-BUY STOCKS-##################################################
while True: # will break when I don't want the bot to buy more stocks
    account = api.get_account() # refresh account info

    if buy_stocks_list: # check if there are stocks to buy

        for stock in buy_stocks_list:
            """
            This loop ensures that we buy a similar ratio of each stock rather than buying the same quantity of each stock.
            If one stock has a price of $1000 and one has a price of $100, for example, we don't want ten shares of each stock.
            We'd rather have one share of stock one and ten shares of stock two to ensure our portfolio is more diversified
            """
            barset = api.get_barset(stock, '1Min', limit=1)
            stock_price = barset[stock][0].c #get current price
            equity_limit = 1000 # maximum equity you want to own of each stock
            buy_qty = 0

            while equity_limit > stock_price:
                buy_qty += 1 # increase buy quantity
                equity_limit -= stock_price # decrease equity_limit variable by the stock price after each iteration

            # the following is currently not being used, but I will leave it here in case I want to use it again
            # if equity_limit < float(account.buying_power):
            #     buy_qty = math.floor(float(account.buying_power)/stock_price) # buy maximum number of stocks available with our buying power
            # else:
            #     pass

            try:
                # submit order for each stock in loop w/ our qty determined by our ratio calculator above
                api.submit_order(
                    symbol=stock,
                    qty=buy_qty,
                    side='buy',
                    type='market',
                    time_in_force='gtc'
                )
                print(f'{buy_qty} shares of {stock} will be bought')

            except (tradeapi.rest.APIError):
                print("Insufficient buying power for best available stocks")
                break

    else:
        print("Either none of our scanned stocks meet our buying criteria or you don't have sufficient buying power")
        break
    break
