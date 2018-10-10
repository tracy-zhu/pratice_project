#coding:utf-8
import sys
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub, SubscribeListener
import threading
import time

def initialization_config():
    pnconfig = PNConfiguration()
    pnconfig.subscribe_key = "sub-c-52a9ab50-291b-11e5-baaa-0619f8945a4f"#Bitflyerのsubscribe_key
    pnconfig.ssl = False
    pubnub = PubNub(pnconfig)
    return pubnub


class MySubscribeListener(SubscribeListener):

    def message(self, pubnub, message):
        global executions
        global ticker
        global board_chg
        executions_CHANNEL = 'lightning_executions_FX_BTC_JPY'
        ticker_CHANNEL = 'lightning_ticker_FX_BTC_JPY'
        board_chg_CHANNEL = 'lightning_board_FX_BTC_JPY'
        if message.channel == executions_CHANNEL:
            executions = message.message
        elif message.channel == ticker_CHANNEL:
            ticker = message.message
        elif message.channel == board_chg_CHANNEL:
            board_chg = message.message

def receive_market(CHANNEL_LIST):
    pubnub = initialization_config()
    mySubscribeListener = MySubscribeListener()
    pubnub.add_listener(mySubscribeListener)
    pubnub.subscribe().channels(CHANNEL_LIST).execute()

def start():
    channels = [
        'lightning_executions_FX_BTC_JPY',
        'lightning_ticker_FX_BTC_JPY',
        'lightning_board_FX_BTC_JPY'
    ]
    receive_market(channels)

if __name__ == '__main__':
    threading.Thread(target=start).start()
    print(executions)
    print(ticker)
    print(board_chg)
    
