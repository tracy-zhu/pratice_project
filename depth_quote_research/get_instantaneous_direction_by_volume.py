# encoding: utf-8
"""
Created on Mon Apr 10 14:49:45 2017

# 脚本用于根据当前的深度行情的挂单量，判断短时间的一个方向
# 盈利几个点就跑
# direction = 0 buy
# direction = 1 sell

@author: Tracy Zhu
"""

### 导入系统库
import sys, time
import logging

reload(sys)

### 导入用户库
sys.path.append("..")
from python_base.open_price_algorithm import *

### 设置日志文件
log_file_name = "mbl_quote.log"
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s  %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    filename=log_file_name,
                    filemode='w')
#定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
#formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
formatter = logging.Formatter('%(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

logging.info(u"开始 mbl quote analyse...")
time.clock()
#########################

# 定义 环境变量
# 策略运行错误
S_Error = 0
# 策略装载
S_Loading = 1
# 开仓中
S_Opening = 2
# 持仓中
S_Position = 3
# 平仓中
S_Closing = 4

# 策略全局变量
g_status = S_Loading
g_direction = 0
open_price = 0

now = datetime.now()
# trading_day = now.strftime('%Y%m%d')
trading_day = '20170407'
to_deal_file_folder = 'E:\\quote_data\\depth_quote_after_auction\\' + trading_day + '\\'
span_num = 5
LIMIT_RATIO = 3
instrument_id = 'RB1710'

output_file_map={}

# 统一买卖报单
def get_plot_arr(bid_price_dict, ask_price_dict, max_price, min_price, tick):
    max_bid_price = max(bid_price_dict.keys())
    min_ask_price = min(ask_price_dict.keys())
    bid_price_series = range(int(max_bid_price) - span_num * int(tick), int(max_bid_price) + int(tick), int(tick))
    ask_price_series = range(int(min_ask_price), int(min_ask_price) + (span_num + 1) * int(tick), int(tick))

    bid_volume_list = []
    ask_volume_list = []
    for price in bid_price_series:
        if bid_price_dict.has_key(price):
            bid_volume_list.append(bid_price_dict[price])
        else:
            bid_volume_list.append(0)

    for price in ask_price_series:
        if ask_price_dict.has_key(price):
            ask_volume_list.append(ask_price_dict[price])
        else:
            ask_volume_list.append(0)

    bid_volume_arr = np.array(bid_volume_list)
    ask_volume_arr = np.array(ask_volume_list)
    bid_price_arr = np.array(bid_price_series)
    ask_price_arr = np.array(ask_price_series)
    return bid_volume_arr, ask_volume_arr, bid_price_arr, ask_price_arr


# 根据深度买卖挂单量判断短时间走势
def get_instantaneous_direction_by_volume(buy_line,sell_line):
    direction = None
    buy_item_list = buy_line[:-1].split(",")
    sell_item_list = sell_line[:-1].split(",")

    instrument_id = buy_item_list[0]
    variety_id = get_variety_id(instrument_id)
    tick, _, _ = get_variety_information(variety_id)
    update_time = buy_item_list[1].split('.')
    update_time_str = "$".join(update_time[0].split(':')) + '$' + update_time[1]

    max_price = 0
    min_price = 9999999

    bid_price_dict = dict()
    ask_price_dict = dict()

    for bid_index in range(1, len(buy_item_list)/2):
        bid_price = float(buy_item_list[bid_index*2])
        bid_volume = int(buy_item_list[bid_index*2+1])
        bid_price_dict[bid_price] = bid_volume

        if bid_price > max_price:
            max_price = bid_price
        if bid_price < min_price:
            min_price = bid_price

    for ask_index in range(1, len(sell_item_list)/2):
        ask_price = float(sell_item_list[ask_index*2])
        ask_volume = int(sell_item_list[ask_index*2+1])
        ask_price_dict[ask_price] = ask_volume

        if ask_price > max_price:
            max_price = ask_price
        if ask_price < min_price:
            min_price = ask_price

    bid_volume_arr, ask_volume_arr, bid_price_arr, ask_price_arr = get_plot_arr(bid_price_dict, ask_price_dict, max_price, min_price, tick)
    if float(sum(bid_volume_arr)) / float(sum(ask_volume_arr)) > LIMIT_RATIO:
        direction = 0
    elif float(sum(ask_volume_arr)) / float(sum(bid_volume_arr)) > LIMIT_RATIO:
        direction = 1

    return direction


def get_update_time(buy_line):
    buy_item_list = buy_line[:-1].split(",")
    update_time = buy_item_list[1]
    return update_time


# 获取状态中文名称
def get_status(status):
    if status == S_Error:
        return "策略运行错误"
    elif status == S_Loading:
        return "策略装载"
    elif status == S_Opening:
        return "开仓中"
    elif status == S_Position:
        return "持仓中"
    elif status == S_Closing:
        return "平仓中"

def get_direction_str(direction):
    if direction == 0:
        return "long"
    elif direction == 1:
        return "short"

def change_status(new_status):
    global g_status
    print u"策略状态由["+ get_status(g_status) + u"]转换成[" + get_status(new_status) + u"]"
    g_status = new_status

def result_file_output(result_file, g_status, price, direction):
    status_str = ''
    direction_str = get_direction_str(direction)
    if g_status == S_Loading:
        status_str = 'open'
    elif g_status == S_Position:
        status_str = 'close'

    str_line = str(status_str) + ',' + str(price) + ',' + str(direction_str) + '\n'
    result_file.write(str_line)


#主函数，参数 mbl 原始文件
def main_deal_func(instrument_id):
    global g_direction, open_price
    sum_profit = 0
    mbl_quote_file_name = to_deal_file_folder + '\\' + instrument_id + '.txt'
    result_file_name = to_deal_file_folder + '\\' + instrument_id + '_result_file.txt'
    mbl_quote_file = open(mbl_quote_file_name,"r")
    result_file = open(result_file_name, 'wb')
    all_lines = mbl_quote_file.readlines()
    line_total_count = len(all_lines)
    loop_total_count = int (line_total_count / 2)

    logging.info("total line: %d",line_total_count)
    # 一次数据两行，买一行，卖一行
    for i in range(1, loop_total_count):
        buy_line = all_lines[i * 2]
        sell_line = all_lines[i * 2 + 1]
        bid_price = buy_line[:-1].split(",")[2]
        ask_price = sell_line[:-1].split(",")[2]
        update_time = get_update_time(buy_line)
        logging.info("plot time: %s", update_time)
        direction = get_instantaneous_direction_by_volume(buy_line, sell_line)

        if g_status == S_Loading:
            if direction == 0:
                open_price = ask_price
                g_direction = 0
                result_file_output(result_file, g_status, open_price, direction)
                change_status(S_Position)
            elif direction == 1:
                open_price = bid_price
                g_direction = 1
                result_file_output(result_file, g_status, open_price, direction)
                change_status(S_Position)

        if g_status == S_Position:
            if direction != g_direction:
                if g_direction == 0 and direction == 1:
                    close_price = bid_price
                    profit = float(close_price) - float(open_price)
                    result_file_output(result_file, g_status, close_price, direction)
                    sum_profit = sum_profit + profit
                    change_status(S_Loading)
                elif g_direction == 1 and direction == 0:
                    close_price = ask_price
                    result_file_output(result_file, g_status, close_price, direction)
                    profit = float(open_price) - float(close_price)
                    sum_profit = sum_profit + profit
                    change_status(S_Loading)

    print sum_profit

    mbl_quote_file.close()
    result_file.close()


#主函数调用
main_deal_func(instrument_id)


#########################
end_time = time.clock()
logging.info(u"end 共耗时: %s",end_time)
