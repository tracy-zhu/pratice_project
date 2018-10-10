# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 14:49:45 2017

# 该脚本用于集合竞价的深度行情展示

@author: Tracy Zhu
"""

### 导入系统库
import sys,string,os,copy,time,types 
import logging

### 导入用户库
sys.path.append("..")
sys.path.append("C:\\Users\\Tracy Zhu\\Desktop\\tool\\open_price_strategy")
from open_price_algorithm import *

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
now = datetime.now()
output_file_map={}

# 统一买卖报单
def unify_bid_ask_price(bid_price_dict, ask_price_dict, max_price, min_price, tick):
    price_range = range(int(min_price), int(max_price)+int(tick), int(tick))
    for price in price_range:
        if not bid_price_dict.has_key(price) and ask_price_dict.has_key(price):
            bid_price_dict[price] = 0
        if not ask_price_dict.has_key(price) and bid_price_dict.has_key(price):
            ask_price_dict[price] = 0

    open_price, _, _, _, _ = get_open_price(bid_price_dict, ask_price_dict, max_price, min_price, tick)
    price_series = range(int(open_price) - span_num * int(tick), int(open_price) + (span_num+1) * int(tick), int(tick))

    bid_volume_list = []
    ask_volume_list = []
    for price in price_series:
        if bid_price_dict.has_key(price):
            bid_volume_list.append(bid_price_dict[price])
        else:
            bid_volume_list.append(0)

        if ask_price_dict.has_key(price):
            ask_volume_list.append(ask_price_dict[price])
        else:
            ask_volume_list.append(0)

    bid_volume_arr = np.array(bid_volume_list)
    ask_volume_arr = np.array(ask_volume_list)
    price_arr = np.array(price_series)
    return bid_volume_arr, ask_volume_arr, price_arr

# 画出柱状图
def bar_advanced_plot(bid_volume_arr, ask_volume_arr, price_arr, update_time_str):
    bar_width = 0.8
    fig = plt.figure()
    fig.set_size_inches(23.2, 14.0)
    ax = fig.add_subplot(1,1,1)
    ax.bar(price_arr, -bid_volume_arr, width=bar_width, alpha=0.4, color="b", label="bid_volume")
    ax.bar(price_arr, ask_volume_arr, width=bar_width, alpha=0.4, color="r", label="ask_volume")

    ax.legend(loc="upper left", shadow=True)
    out_file_folder = depth_picture_folder + instrument_id + "\\"
    isExists = os.path.exists(out_file_folder)
    if not isExists:
        os.makedirs(out_file_folder)
    out_file_name = out_file_folder + update_time_str + ".png"
    plt.savefig(out_file_name)
    plt.close('all')
    return


#画出一次买卖行情数据
def plot_depth_quote(buy_line,sell_line):  
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

    bid_volume_arr, ask_volume_arr, price_arr = unify_bid_ask_price(bid_price_dict, ask_price_dict, max_price, min_price, tick)
    bar_advanced_plot(bid_volume_arr, ask_volume_arr, price_arr, update_time_str)


def get_update_time(buy_line):
    buy_item_list = buy_line[:-1].split(",")
    update_time = buy_item_list[1]
    return update_time


#主函数，参数 mbl 原始文件
def main_deal_func(instrument_id):
    mbl_quote_file_name = to_deal_file_folder + '\\' + instrument_id + '.txt'
    mbl_quote_file = open(mbl_quote_file_name,"r")
    all_lines = mbl_quote_file.readlines()
    line_total_count = len(all_lines)
    loop_total_count = int (line_total_count / 2)
    
    logging.info("total line: %d",line_total_count)
    # 一次数据两行，买一行，卖一行
    for i in range(1, loop_total_count):
        first_line = all_lines[i * 2]
        next_line = all_lines[i * 2 + 1]
        buy_price = first_line[:-1].split(",")[2]
        sell_price = next_line[:-1].split(",")[2]
        if buy_price > sell_price:
            buy_line = all_lines[i*2]
            sell_line = all_lines[i*2+1]
            update_time = get_update_time(buy_line)
            logging.info("plot time: %s", update_time)
            plot_depth_quote(buy_line, sell_line)
    mbl_quote_file.close()

        
#主函数调用
if __name__ == '__main__':
    # trading_day = now.strftime('%Y%m%d')
    trading_day = '20170614'
    to_deal_file_folder = 'E:\\quote_data\\depth_quote\\' + trading_day + '\\'
    depth_picture_folder = 'E:\\quote_data\\depth_quote_picture\\' + trading_day + '\\'
    isExists = os.path.exists(depth_picture_folder)
    if not isExists:
        os.makedirs(depth_picture_folder)
    span_num = 30
    instrument_id = 'PB1707'
    main_deal_func(instrument_id)


#########################
end_time = time.clock()
logging.info(u"end 共耗时: %s",end_time)
