# -*- coding: utf-8 -*-
"""

# 本文件包含了画图中的常用函数
# 给定两个合约，一张图上画出两个合约的价格
# 按照价位画出每个合约的成交密集区
# 按照时间画出每个合约的成交密集区

Tue 2016/10/11

@author: Tracy Zhu
"""

from python_base.common_method import *
import matplotlib.pyplot as plt
from matplotlib import gridspec


# ----------------------------------------------------------------------
# 给定一个品种和交易日，画出当天主力和次主力之间的价差关系图
def get_spread_array_map(variety_id, trading_day, tick_num):
    instrument_file_list = get_instrument_file_list(str(trading_day))
    instrument_list = instrument_file_list[variety_id]
    main_instrument_id, sub_instrument_id = get_main_instrument_id(instrument_list)
    first_file_name = G_TICK_QUOTE_FILE_ROOT_FOLDER + "\\" + str(trading_day) + "\\" + main_instrument_id + ".csv"
    second_file_name = G_TICK_QUOTE_FILE_ROOT_FOLDER + "\\" + str(trading_day) + "\\" + sub_instrument_id + ".csv"
    first_instrument = first_file_name.split('\\')[-1].split('.')[0]
    second_instrument = second_file_name.split('\\')[-1].split('.')[0]
    data_first = pd.read_csv(first_file_name, header=0, names=G_TICK_COLUMNS, index_col=False)
    data_second = pd.read_csv(second_file_name, header=0, names=G_TICK_COLUMNS, index_col=False)
    df_first = get_dataframe(data_first, G_TICK_COLUMNS)
    df_second = get_dataframe(data_second, G_TICK_COLUMNS)
    spread_array_last = df_first.Last_Price - df_second.Last_Price
    spread_array = spread_array_last[spread_array_last.index.hour >= 20].head(tick_num)
    last_spread_array = df_first.Pre_Close_Price - df_second.Pre_Close_Price
    last_spread = last_spread_array[spread_array_last.index.hour >= 20].head(tick_num)
    # spread_array_close = df_first.Bid_Price1 - df_second.Ask_Price1
    fig = plt.figure()
    fig.set_size_inches(23.2, 14.0)
    ax = fig.add_subplot(1, 1, 1)
    out_title = 'Contract Spread array of ' + first_instrument + '&' + second_instrument + ' in ' + str(trading_day)
    ax.set_title(out_title)
    ax.plot(spread_array, color='b', label='spread_array', linewidth=2)
    ax.plot(last_spread, color='r', label='last_spread', linewidth=2)
    ax.legend(loc='upper left')
    # ax.plot(spread_array_close, 'r', label='spread_array_close')
    path_name = OUT_FILE_FOLDER + str(trading_day)
    isExists = os.path.exists(path_name)
    if not isExists:
        os.makedirs(path_name)
    out_file_name = path_name + '\\' + first_instrument + '&' + second_instrument + ' in ' + str(
        trading_day) + '.png'
    plt.savefig(out_file_name)

# ----------------------------------------------------------------------
# 该程序绘出了交易量随价格变化的图形
def get_trade_volume_analysis(instrument_id, trading_day, pre_trading_day):
    one_file_name = G_TICK_QUOTE_FILE_ROOT_FOLDER + "\\" + trading_day + "\\" + instrument_id + ".csv"
    pre_one_file_name = G_TICK_QUOTE_FILE_ROOT_FOLDER + "\\" + pre_trading_day + "\\" + instrument_id + ".csv"
    quote_data = pd.read_csv(one_file_name, header=0, index_col=False, names=G_TICK_COLUMNS)
    pre_quote_data = pd.read_csv(pre_one_file_name, header=0, index_col=False, names=G_TICK_COLUMNS)
    price_array = quote_data.close.unique()

    price_map = dict()
    for price in price_array:
        quote_data_temp = pre_quote_data[pre_quote_data.close == price]
        pre_trade_volume = sum(quote_data_temp.trade_volume)
        quote_data_temp = quote_data[quote_data.close == price]
        trade_volume = sum(quote_data_temp.trade_volume)
        volume = [pre_trade_volume, trade_volume]
        if price_map.has_key(price):
            pass
        else:
            price_map[price] = []
            price_map[price].append(volume)

    max_price = max(price_map.keys())
    min_price = min(price_map.keys())
    title = trading_day + ' ' + instrument_id
    x = price_map.keys()
    x.sort()
    y = []
    z = []
    for price in x:
        y.append(price_map[price][0][0])
        z.append(price_map[price][0][1])

    gs = gridspec.GridSpec(1, 2, width_ratios=[1, 4])
    ax0 = plt.subplot(gs[0])
    ax0.plot(y, x, color='r', label='pre_trade_volume', linewidth=2)
    ax0.plot(z, x, color='g', label='trade_volume', linewidth=2)
    plt.ylim([min_price, max_price])
    ax0.legend(loc='upper left')
    ax1 = plt.subplot(gs[1])
    ax1.plot(quote_data.close, label='price')
    plt.ylim([min_price, max_price])
    ax1.set_title(title)
    plt.subplots_adjust(wspace=0, hspace=0)
    ax1.legend(loc='upper left')
    out_file_name = OUT_FILE_FOLDER + title + '.png'
    plt.savefig(out_file_name)
