import pybitflyer
import json
import requests
import time
import hmac
import hashlib
api = pybitflyer.API(api_key="362q3qHwsQaAaY3cgdvaJM", api_secret="Wpd9GQ3W4jCOc18IxFjFngxNWr2zxxoz8z8m9LcvKx8=")

def main():
    FXBTC=api.board(product_code="FX_BTC_JPY")
    FXBTC_ask=FXBTC['asks'][0]['price']
    FXBTC_bid=FXBTC['bids'][0]['price']
    BTC=api.board(product_code="BTC_JPY")['mid_price']
    spread=(FXBTC_ask/BTC)-1
    class bitflyerApi:
        def __init__(self):
            self.api_key = '362q3qHwsQaAaY3cgdvaJM'
            self.api_secret = 'Wpd9GQ3W4jCOc18IxFjFngxNWr2zxxoz8z8m9LcvKx8='
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
        def order(data):
            api = bitflyerApi()
            result = api.post_api_call('/v1/me/sendchildorder',data).json()
            return result
        def cancel(data):
            api = bitflyerApi()
            result = api.post_api_call('/v1/me/cancelchildorder',data).json()
            return result
        def get_order():
            api = bitflyerApi()
            result = api.get_api_call('/v1/me/getchildorders?product_code=FX_BTC_JPY&child_order_state=ACTIVE').json()
            return result
        def get_positions():
            api = bitflyerApi()
            result = api.get_api_call('/v1/me/getpositions?product_code=FX_BTC_JPY').json()
            return result
    params_buy={"product_code": "FX_BTC_JPY","child_order_type": "LIMIT","side": "BUY","price": FXBTC_bid + 10,"size": 0.001,"minute_to_expire": 1}
    params_sell={"product_code": "FX_BTC_JPY","child_order_type": "LIMIT","side": "SELL","price": FXBTC_ask - 10,"size": 0.001,"minute_to_expire": 1}

    get_order=bitflyerApi.get_order()
    cancel_para={"product_code": "FX_BTC_JPY","child_order_acceptance_id": "JRF20180222-162225-996733"}
    cancel=bitflyerApi.cancel(cancel_para)
    get_position=bitflyerApi.get_positions()
    position_limit = 0
    if len(get_position) > 0:
        for position_dict in get_position:
            position_limit += position_dict['size']


    if spread > 0.2 and position_limit > -0.01:
        order=bitflyerApi.order(params_sell)
    elif spread < 0.2 and position_limit < 0:
        order=bitflyerApi.order(params_buy)


if __name__ == '__main__':
    while True:
        main()
        time.sleep(1)

