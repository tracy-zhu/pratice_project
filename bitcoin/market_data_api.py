# -*- coding: utf-8 -*-
"""

# 用于测试行情接口

# 参考 https://fx.ichizo.biz/2017/05/09/bitflyer-futures.html

Tue 2018/02/23

@author: Tracy Zhu
"""

from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub, SubscribeListener
from pandas import DataFrame, Series
import json
import requests
import time
import hmac
import hashlib
# import util

class bitflyerApi:
    def __init__(self):
        self.api_key = 'APIキー'
        self.api_secret = 'APIシークレットキー'
        self.api_endpoint = 'https://api.bitflyer.jp'

    def get_api_call(self,path):
        method = 'GET'
        timestamp = str(time.time())
        text = timestamp + method + path
        sign = hmac.new(bytes(self.api_secret.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()
        request_data=requests.get(
        self.api_endpoint+path
        ,headers = {
        'ACCESS-KEY': self.api_key,
        'ACCESS-TIMESTAMP': timestamp,
        'ACCESS-SIGN': sign,
        'Content-Type': 'application/json'
        })
        return request_data

    def post_api_call(self,path,body):
        body = json.dumps(body)
        method = 'POST'
        timestamp = str(time.time())
        text = timestamp + method + path + body
        sign = hmac.new(bytes(self.api_secret.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()
        request_data=requests.post(
        self.api_endpoint+path
        ,data= body
        ,headers = {
        'ACCESS-KEY': self.api_key,
        'ACCESS-TIMESTAMP': timestamp,
        'ACCESS-SIGN': sign,
        'Content-Type': 'application/json'
        })
        return request_data

    """
    channel: 'lightning_ticker_BTC_JPY'
    """
    def pubnub_call(self,channel):
        pnconfig = PNConfiguration()
        pnconfig.subscribe_key = "sub-c-52a9ab50-291b-11e5-baaa-0619f8945a4f"
        pnconfig.ssl = False
        pubnub = PubNub(pnconfig)
        my_listener = SubscribeListener()
        pubnub.add_listener(my_listener)
        pubnub.subscribe().channels(channel).execute()
        my_listener.wait_for_connect()
        while True:
            bf_result = my_listener.wait_for_message_on(channel)
            bf_data = bf_result.message
            print bf_data
        # pubnub.unsubscribe().channels(channel).execute()
        # my_listener.wait_for_disconnect()
            return bf_data
        
    def get_board(self):
        api = bitflyerApi()
        result = api.pubnub_call('lightning_board_FX_BTC_JPY')
        print(result)
        # bids = util.util.dict_to_pd(result['bids'],'bf',False)
        # asks = util.util.dict_to_pd(result['asks'],'bf',True)
        bids = DataFrame(result['bids'])
        asks = DataFrame(result['asks'])
        return bids,asks

    def get_balance(self):
        api = bitflyerApi()
        result = api.get_api_call('/v1/me/getbalance').json()
        data = {}
        for row in result:
            if (row['currency_code'] == 'JPY'):
                data['jpy_amount'] = float(row['amount'])
                data['jpy_available'] = float(row['available'])
            elif (row['currency_code'] == 'BTC'):
                data['btc_amount'] = float(row['amount'])
                data['btc_available'] = float(row['available'])
        return data

    def order(self,data):
        api = bitflyerApi()
        result = api.post_api_call('/v1/me/sendchildorder',data).json()
        return result

if __name__ == '__main__':
    channel = 'lightning_board_snapshot_FX_BTC_JPY'
    market_data_api = bitflyerApi()
    result = market_data_api.get_board()

