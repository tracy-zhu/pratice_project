import pybitflyer
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub_tornado import PubNubTornado
from pubnub.pnconfiguration import PNReconnectionPolicy
from tornado import gen
import time
import threading
import numpy as np
c = PNConfiguration()
c.subscribe_key = 'sub-c-52a9ab50-291b-11e5-baaa-0619f8945a4f'
c.reconnect_policy = PNReconnectionPolicy.LINEAR
pubnub = PubNubTornado(c)
api = pybitflyer.API()
fx_price = api.ticker(product_code="FX_BTC_JPY")["ltp"]
btc_price = api.ticker(product_code="BTC_JPY")["ltp"]
disparity_list = []
order = Order()
lot = 0.001
maxlot = 0.01
pos = 0
@gen.coroutine

def main(channels):
    class Callback(SubscribeCallback):
        def message(self, pubnub, message):
            global disparity_list
            global fx_price
            global btc_price
            FX_CHANNEL = 'lightning_executions_FX_BTC_JPY'
            BTC_CHANNEL = 'lightning_executions_BTC_JPY'
            if message.channel == FX_CHANNEL:
                fx_price = message.message[0]["price"]
            elif message.channel == BTC_CHANNEL:
                btc_price = message.message[0]["price"]
            price_disparity = fx_price/btc_price * 100 - 100
            disparity_list.append(price_disparity)

            return price_disparity

    s = Callback()
    pubnub.add_listener(s)
    pubnub.subscribe().channels(channels).execute()

if __name__ == '__main__':
    channels = [
        'lightning_executions_FX_BTC_JPY',
        'lightning_executions_BTC_JPY'
    ]
    main(channels)
    pubnub_thread = threading.Thread(target=pubnub.start)
    pubnub_thread.start()
    while len(disparity_list) == 0:
        continue
    while True:
        health = api.gethealth(product_code="FX_BTC_JPY")
        healthy = health != "SUPER BUSY" and health != "STOP"
        present_lot = pos * lot
        if disparity_list[-1] > 10.05 and present_lot > -maxlot and healthy:
            order.market(side="SELL", size=lot)
            pos -= 1
        elif disparity_list[-1] < 9.95 and present_lot < maxlot and healthy:
            order.market(side="BUY", size=lot)
            pos += 1
        #superbusyのとき強制決済
        elif healthy != True:
            present_lot = api.getpositions(product_code="FX_BTC_JPY")
            pos_sum = 0
            for i in present_lot:
                if i["side"] == "BUY":
                    pos_sum += i["size"]
                elif i["side"] == "SELL":
                    pos_sum -= i["size"]
            if pos_sum > 0:
                order.market(side="SELL", size=pos_sum)
            elif pos_sum < 0:
                order.market(side="BUY", size=pos_sum)
            else:
                pass
        time.sleep(1)