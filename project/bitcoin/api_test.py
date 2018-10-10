#coding:utf-8
import sys
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub, SubscribeListener


def initialization_config():
    pnconfig = PNConfiguration()
    pnconfig.subscribe_key = "sub-c-52a9ab50-291b-11e5-baaa-0619f8945a4f"#Bitflyerのsubscribe_key
    pnconfig.ssl = False
    pubnub = PubNub(pnconfig)
    return pubnub


class MySubscribeListener(SubscribeListener):

    def message(self, pubnub, message):
        str_line = ''
        if type(message.message) == dict:
            if len(message.message) == 3:
                "order book update"
                print "order book updates + "
                print message.message
            else:
                "ticker"
                print 'ticker + '
                print message.message
        elif type(message.message) == list:
            "executions"
            print 'executions + '
            print message.message


    def process_signal_executions(self, executions):
        "处理executions信号函数"
        total_bid_volume = 0
        total_ask_volume = 0
        turnover = 0
        for each_execution in executions:
            side = each_execution['side']
            if side == "SELL":
                total_ask_volume += each_execution['size']
            elif side == "BUY":
                total_bid_volume += each_execution['size']
            turnover += each_execution['size'] * each_execution['price']
        vwap = turnover / (total_ask_volume + total_bid_volume)
        return vwap, total_bid_volume, total_ask_volume


    def process_signal_ticker(self, ticker):
        "处理ticker信号函数"
        ticker_line = ticker_process(ticker)
        mid_price = (ticker['best_bid'] + ticker['best_ask']) / 2
        self.mid_price_list.append(mid_price)
        return ticker_line


    def process_signal_board(self, board):
        "处理board函数"
        print "board + \n" 
        print board

    def signal_compound(self):
        mid_price_momentum = 0
        if len(self.mid_price_list) == 5:
            mid_price_momentum = self.mid_price_list[-1] - self.mid_price_list[0]
        signal = 0.4 * mid_price_momentum
        return signal


def receive_market(CHANNEL_LIST):
    pubnub = initialization_config()
    mySubscribeListener = MySubscribeListener()
    pubnub.add_listener(mySubscribeListener)
    pubnub.subscribe().channels(CHANNEL_LIST).execute()


if __name__ == '__main__':
    # CHANNEL_LIST = ['lightning_executions_FX_BTC_JPY', 'lightning_ticker_FX_BTC_JPY', 'lightning_board_FX_BTC_JPY']
    CHANNEL_LIST = ['lightning_executions_FX_BTC_JPY', 'lightning_ticker_FX_BTC_JPY']
    receive_market(CHANNEL_LIST)
