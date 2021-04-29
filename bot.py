# IMPORTING LIBRARIES

import websocket, json, talib
import numpy as np 
import config
from binance.client import Client
from binance.enums import *

# TRADING STRATERGY CONSTANTS

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'BTCUSDT'
TRADE_QUANTITY = 0.00018

close_prices = []   # closing price of each candle received
SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"
coins_bought = False  # used to check if we already bought coin in overbought or oversell condition, otherwise we will keep on buying it again and again till the time it is overbought or oversold

client = Client(config.API_KEY, config.API_SECRET, tld='com')

def order(side, quantity, symbol,order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as error_occured:
        print("An error occured - {}".format(error_occured))
        return False
    return True

def on_open(web_socket):
    print("Connection opened successfully")

def on_close(web_socket):
    print("Connection closed successfully")

def on_message(web_socket, message):
    print("candle received")
    json_message = json.loads(message)
    candle = json_message['k']
    close_status = candle['x']
    close_price = candle['c']

    if close_status:
        print("candle closed at {}".format(close_price))
        close_prices.append(float(close_price))
        print(close_prices)

        if len(close_prices) > RSI_PERIOD:
            arr = np.array(close_prices)
            rsi = talib.RSI(arr, RSI_PERIOD)
            print("RSI Array : ")
            print(rsi)
            latest_rsi = rsi[-1]
            print("Latest RSI Calculated : {}".format(float(latest_rsi)))

            if float(latest_rsi) > RSI_OVERBOUGHT:
                if coins_bought:
                    print("It is overbought, Selling now")
                    order_status = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)   # placing sell order
                    if order_status:
                        coins_bought = False
                else:
                    print("It is overbought, but you have nothing to sell")

            if float(latest_rsi) < RSI_OVERSOLD:
                if coins_bought:
                    print("It is oversold, but you already own it")
                else:
                    print("It is oversold, Buying now")
                    order_status = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)   # placing buy order
                    if order_status:
                        coins_bought = True

web_socket = websocket.WebSocketApp(SOCKET, on_open = on_open, on_close = on_close, on_message = on_message)
web_socket.run_forever()