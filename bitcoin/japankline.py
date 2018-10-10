# -*- coding: utf-8 -*-

import requests
import pandas as pd
depth_fly = {'product_code': 'FX_BTC_JPY'}
url_fly = "https://api.bitflyer.jp"
path_fly="/v1/board"
g1_fly = requests.get(url_fly + path_fly , params=depth_fly)
depth_data_fly=g1_fly.json()
mid_price = depth_data_fly["mid_price"]
best_bid_price = depth_data_fly["bids"][0]['price']
best_ask_price = depth_data_fly["asks"][0]['price']
bid_ask_spread = best_ask_price - best_bid_price

print "mid price is " + str(mid_price)
print "best bid price is " + str(best_bid_price)
print "best ask price is " + str(best_ask_price)
print "bid ask spread is " + str(bid_ask_spread)
# ask_fly=depth_data_fly['asks']
# bid_fly=depth_data_fly['bids'][0]['price']

