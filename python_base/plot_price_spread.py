# -*- coding: utf-8 -*-
"""

# 用于将不同品种之间的价差关系画出来

Tue 2017/3/14

@author: Tracy Zhu
"""
# 导入系统库
import logging
from pylab import *
import os
import sys

mpl.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
mpl.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题
# 导入用户库：：
sys.path.append("..")
from python_base.plot_method import *

trading_day_list = get_trading_day_list()

def get_price_spread(variety_id, begin_date, end_date):
    price_spread_list = []
    day_list = []

    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        if begin_date <= trading_day <= end_date:
            instrument_file_list = get_instrument_file_list(trading_day)
            if instrument_file_list.has_key(variety_id):
                instrument_list = instrument_file_list[variety_id]
                main_instrument_id, second_instrument_id = get_main_instrument_id(instrument_list)
                day_list.append(trading_day)
                first_close_price = get_close_price(main_instrument_id, trading_day)
                second_close_price = get_close_price(second_instrument_id, trading_day)
                price_spread = first_close_price - second_close_price
                price_spread_list.append(price_spread)

    return day_list, price_spread_list

def draw_price_spread(variety_id, x_list, y_list):
    x_length = len(x_list)
    if x_length <= 50:
        times_delta = 1
    elif x_length <= 90:
        times_delta = 3
    else:
        times_delta = 4
    # 处理横坐标的标签
    group_labels = []
    i = 0
    for index in range(x_length):
        if i % times_delta == 0:
            group_labels.append(x_list[index])
        else:
            group_labels.append('')
        i += 1

    # xy标签
    plt.xlabel(u"日期")
    plt.ylabel(u"价格")
    # 标题
    title11 = variety_id + u"的价差曲线"
    plt.title(title11)

    x_list_last = range(0, len(y_list))

    # group_labels = x_list

    plt.plot(x_list_last, y_list, 'b', linewidth=0.5)

    # 横坐标设置(坐标代替,倾斜度)
    plt.xticks(x_list_last, group_labels, rotation=30)
    # 网格线
    plt.grid()

    now_path = os.getcwd()
    # print now_path
    save_pic_path = now_path + '\\picture'
    try:
        os.mkdir(save_pic_path)
    except:
        pass
    save_pic_name = save_pic_path + '\\' + '_k_line' + '.jpg'
    savefig(save_pic_name)

    plt.show()

if __name__ == '__main__':
    variety_id = "RB"
    begin_date = '20160101'
    end_date = '20161231'
    day_list, price_spread_list = get_price_spread(variety_id, begin_date, end_date)
    draw_price_spread(variety_id, day_list, price_spread_list)