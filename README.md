# Swing-Trading-Stock-Bot

## Project Overview
A Python-based bot that uses the Alpaca API and swing trading principles to buy and sell securities. This bot has four scripts - one that scrapes data and calculates technical indicators, one that buys securities, one that sells securities, and a final script that calls the other scripts in a loop to run constantly. Currently, the bot buys and sells based on indicators that I pass to it. The bot currently only paper trades as I'd like to make sure there are absolutely no bugs that will cause issues when I use real money.

## How to Use
1) First, you need an Alpaca Paper Trading account. You can sign up [here](https://app.alpaca.markets/signup)
2) Click "generate new key" on your portfolio page to attain a key and secret key
3) Put the keys into the 'config.py' file in this repository<br>
> the main key is assigned to the APCA_API_KEY_ID variable while the secret key is assigned to APCA_API_SECRET_KEY
4) Run 'biz_bot_final_script.py'

## Tunable Parameters
The indicators I use are based on my personal trading preferences. If you don't like them, that's okay! You can go in and change them however you'd like. Here's where you should look for things you might want to tune to your liking:

Each section has a commented header that describes what the code below it will do - this is how I will reference what to look for.

### **biz_bot_scrape.py**<br>
- GET LIST OF SYMBOLS
>  - Change 'holdings' variable to a different csv
>    - Note: you will likely have to split up the symbols differently in the following line
>  - Change 'limit' in the day_bars_url string to change the number of days you'd like to bring in
- ADDING IN INDICATORS
>  - Here, I use btalib and talib to calculate different SMA lines and RSI - any of these can be changed
>    - Refer to [btalib](https://btalib.backtrader.com/introduction/) and [talib](https://mrjbq7.github.io/ta-lib/doc_index.html) documentation pages for more info on how to do >this
- CALCULATE PIVOT POINT AND RESISTANCE LEVEL
>  - You can add more resistance/support levels as you choose
- FILTER DATA
>  - Here's where you'd change the buying criteria

### **biz_bot_place_orders.py**<br>
- BUY STOCKS
>  - The equity_limit variable ensures stocks will be bought at a somewhat even ratio - this can be changed based on what your buying power is and how much diversification you >want in your portfolio

### **biz_bot_sell.py**<br>
- ADDING IN INDICATORS
>  - Anything you change in the 'scrape' script will also have to be changed here
- CALCULATE PIVOT POINT AND RESISTANCE LEVEL
>  - Anything you change in the 'scrape' script will also have to be changed here
- CRITERIA FOR SELLING
>  - Here's where you'd change the selling criteria
  
## Ideas for future versions
  - Implement a machine learning algorithm to predict stock prices and trade on those predictions in conjunction with some techincal indicators
  - Trade options with the same criteria - would need a different API
  - Find a way to scan more than Alpaca's 200 stock limit at one time<br>
  <br>
This will certainly be a long-term project for me as I look for ways to improve the bot and make it more efficient - if you have any ideas yourself, feel free to submit a pull request or email me at abzdel@bryant.edu. Thank you for your interest!

## Programs & Packages
- **Python**: Version 3.7
- **Packages**: pandas, btalib, talib, requests, json, tradeapi
- **Alpaca**: For scraping stock data and buying/selling securities


