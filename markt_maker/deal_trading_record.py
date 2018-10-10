#  -*- coding: utf-8 -*-
"""

# 本脚本分析每日的成交记录
# 比如间隔多长时间会盈利平仓这种问题
# lost_deal_result 将亏损的序列打印出来
# deal_trading_record 将能够盈利一个点所需要的等待的时常和当中的最大回撤输出出来
  最大回撤是按照对手价计算的

Tue 2017/09/28

@author: Tracy Zhu
"""
# 导入系统库
import sys

# 导入用户库：
sys.path.append("..")
from python_base.plot_method import *

report_file_folder = "..\\markt_maker\\trading_report\\"
instrument_id = 'PB1801'
now = datetime.now()
#trading_day = now.strftime('%Y%m%d')
trading_day = '20171121'
quote_data = read_data(instrument_id, trading_day)
variety_id = get_variety_id(instrument_id)
tick, _, _ = get_variety_information(variety_id)

report_file_name = report_file_folder + trading_day + u"\\成交记录_" + trading_day[2:] + '.csv'
f = open(report_file_name, 'r')


def get_profit_duration(quote_data, deal_price, open_direction, deal_time):
    """
    读取数据文件，计算出等待多久能够盈利一个点出场
    :param deal_price: 成交价
    :param open_direction: 买卖方向，0为买， 1为卖
    :return: 能够盈利一个点出场的等待时间duration
    """
    global tick
    min_bid_price = 999999
    max_ask_price = 0
    max_drawdown = 0
    night_data = quote_data[quote_data.Update_Time >= '20:59:00']
    day_data = quote_data[quote_data.Update_Time < '20:59:00']
    if deal_time[:2] >= '20':
        slice_data = night_data[night_data.Update_Time > deal_time]
    else:
        slice_data = day_data[day_data.Update_Time > deal_time]
    duration = 0
    for index in slice_data.index:
        if duration < 2400:
            if open_direction == 0:
                ask_price = quote_data.Ask_Price1[index]
                duration += 1
                if quote_data.Bid_Price1[index] < min_bid_price:
                    min_bid_price = quote_data.Bid_Price1[index]
                max_drawdown = min_bid_price - int(deal_price)
                if ask_price > deal_price + tick:
                    break
            elif open_direction == 1:
                bid_price = quote_data.Bid_Price1[index]
                duration += 1
                if quote_data.Ask_Price1[index] > max_ask_price:
                    max_ask_price = quote_data.Ask_Price1[index]
                max_drawdown = int(deal_price) - max_ask_price
                if bid_price < deal_price - tick:
                    break
    return duration, max_drawdown


lost_deal_result = '..\\markt_maker\\result\\lost_deal_result_' + trading_day + '.csv'
f2 = open(lost_deal_result, 'wb')
lines = f.readlines()
duration_list = []
max_drawdown_list = []
long_position = 0
long_price_list = []
short_position = 0
short_price_list = []
profit_num = 0
for line in lines[:0:-1]:
    line_list = line.split(',')
    direction, flag, deal_price, _, deal_time = line_list[2:7]
    deal_price = int(deal_price)
    if flag ==  '\xbf\xaa\xb2\xd6':
        print "open"
        if direction == '\xc2\xf2\xa1\xa1':
            "direction is buy"
            open_direction = 0
            long_position += 1
            long_price_list.append(int(deal_price))
            duration, max_drawdown = get_profit_duration(quote_data, deal_price, open_direction, deal_time)
            duration_list.append(duration)
            max_drawdown_list.append(max_drawdown)
            if duration > 1800:
                f2.write(line)
        elif direction == '\xa1\xa1\xc2\xf4':
            "direction is sell"
            open_direction = 1
            short_position += 1
            short_price_list.append(int(deal_price))
            duration, max_drawdown = get_profit_duration(quote_data, deal_price, open_direction, deal_time)
            duration_list.append(duration)
            max_drawdown_list.append(max_drawdown)
            if duration > 1800:
                f2.write(line)
    elif flag == '\xc6\xbd\xbd\xf1':
        print "close"
        if direction == '\xc2\xf2\xa1\xa1':
            "close sell position"
            short_position = short_position - 1
            if int(deal_price) < short_price_list.pop(0):
                profit_num += 1
        elif direction == '\xa1\xa1\xc2\xf4':
            "close buy position"
            long_position = long_position - 1
            if int(deal_price) > long_price_list.pop(0):
                profit_num += 1


duration_series = Series(duration_list)
max_drawdown_series = Series(max_drawdown_list)
concat_series = pd.concat([duration_series, max_drawdown_series], axis=1, keys =['duration', 'max_drawdown'])
duration_series.describe()
result_file_name = "..\\markt_maker\\result\\deal_trading_record_" + trading_day + ".csv"
concat_series.to_csv(result_file_name)
f2.close()


print "profit_num is ", profit_num
print "total trading records is ", len(duration_list)
