import time, config
import datetime, os
import alpaca_trade_api as tradeapi

# run this file in the command line to have the bot automatically buy and sell stocks
api = tradeapi.REST(config.APCA_API_KEY_ID, config.APCA_API_SECRET_KEY, config.APCA_API_BASE_URL) # setup

while True: # continually run through buy and sell scripts
        os.system('biz_bot_place_orders.py')
        os.system('biz_bot_sell.py')
        #print('waiting two minutes')
        time.sleep(60)
        print("-"*50)
        continue
