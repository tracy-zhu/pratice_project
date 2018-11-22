# -*- coding: utf-8 -*-
"""

# 计算期权的数据对大盘有指导意义的指标，报过持仓量，成交量，成交额的put_call_ratio指标

Fri 2018/10/26

@author: Tracy Zhu
"""

import sys

# 导入用户库
sys.path.append("..")
from stock_base.stock_option_base import *
from python_base.plot_method import *

trading_day_list = get_trading_day_list()


def calc_day_put_call_ratio(trading_day):
    """
    计算上证50etf期权某一个交易日的put_call_ratio
    :param trading_day:
    :return:
    """
    volume_call_num = 0
    volume_put_num = 0
    amount_call_num = 0
    amount_put_num = 0
    position_call_num = 0
    position_put_num = 0
    position_pcr = 0
    amount_pcr = 0
    volume_pcr = 0
    file_name_list = filter_option_file(trading_day)
    option_attribute_dict = get_option_attribute(trading_day, file_name_list)
    for file_name, direction_attribute in option_attribute_dict.items():
        print(file_name, direction_attribute)
        result_list = read_option_data(file_name)
        if result_list != None:
            volume = result_list[1]
            amount = result_list[2]
            position = result_list[3]
            if direction_attribute == 'call':
                volume_call_num += volume
                amount_call_num += amount
                position_call_num += position
            elif direction_attribute == 'put':
                volume_put_num += volume
                amount_put_num += amount
                position_put_num += position
    if position_call_num > 0 and amount_call_num > 0 and volume_call_num > 0:
        position_pcr = float(position_put_num) / float(position_call_num)
        amount_pcr = float(amount_put_num) / float(amount_call_num)
        volume_pcr = float(volume_put_num) /float(volume_call_num)
    return position_pcr, amount_pcr, volume_pcr


def calc_pcr_by_daily_data(trading_day):
    """
    根据数据库生成的期权日线数据，计算每天的put call ratio,包括成交量的，持仓量的和成交额的
    :param trading_day:
    :return:
    """
    position_pcr = 0
    amount_pcr = 0
    volume_pcr = 0
    option_daily_df = read_option_data_daily(trading_day)
    call_option_df = option_daily_df[option_daily_df.DELTA > 0]
    put_option_df = option_daily_df[option_daily_df.DELTA < 0]
    volume_call_num = call_option_df.VOLUME.sum()
    volume_put_num = put_option_df.VOLUME.sum()
    amount_call_num = call_option_df.AMT.sum()
    amount_put_num = put_option_df.AMT.sum()
    position_call_num = call_option_df.OI.sum()
    position_put_num = put_option_df.OI.sum()
    if position_call_num > 0 and amount_call_num > 0 and volume_call_num > 0:
        position_pcr = float(position_put_num) / float(position_call_num)
        amount_pcr = float(amount_put_num) / float(amount_call_num)
        volume_pcr = float(volume_put_num) /float(volume_call_num)
    return position_pcr, amount_pcr, volume_pcr


def calc_trading_days_pcr(start_date, end_date):
    """
    计算过去一段交易日期权的pcr指标
    :param start_date:
    :param end_date:
    :return:
    """
    ma_num = 20
    pcr_days_dict = defaultdict()
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        trading_day = change_trading_day_format(trading_day)
        if start_date <= trading_day <= end_date:
            print(trading_day)
            result_pcr = calc_pcr_by_daily_data(trading_day)
            pcr_days_dict[trading_day] = result_pcr
    pcr_days_df = DataFrame(pcr_days_dict).T
    pcr_days_df.columns = ['position_pcr', 'amount_pcr', 'volume_pcr']
    pcr_days_df['ma_position_pcr'] = pcr_days_df['position_pcr'].rolling(window=ma_num).mean()
    pcr_days_df['ma_amount_pcr'] = pcr_days_df['amount_pcr'].rolling(window=ma_num).mean()
    pcr_days_df['ma_volume_pcr'] = pcr_days_df['volume_pcr'].rolling(window=ma_num).mean()
    start_date = pcr_days_df.index[0]
    end_date = pcr_days_df.index[-1]
    index_50_df = get_index_data('000016.SH', start_date, end_date)
    index_50_series = Series(index_50_df.close.values, index=pcr_days_df.index)
    pcr_days_df['50_index'] = index_50_series
    index_50_pct_chg = Series(index_50_df.pct_chg.values, index=pcr_days_df.index)
    pcr_days_df['50_pct_chg'] = index_50_pct_chg
    return pcr_days_df


def plot_index_with_pcr(pcr_days_df):
    """
    将上证50指数的指数线和上面计算的pcr指标放在一起
    用于判断大盘的择时
    :param pcr_days_df:
    :return:
    """
    fig, ax = plt.subplots()
    ax.plot(pcr_days_df['ma_position_pcr'], color='r', label="position pcr")
    ax1 = ax.twinx()
    ax1.plot(pcr_days_df['50_index'], color="b", label="50.SH index")
    ax.legend(loc="upper left")
    ax1.legend(loc="upper right")
    title = "pcr & 50 index"
    plt.title(title)
    fig.set_size_inches(23.2, 14.0)
    return pcr_days_df


def correlation_pcr_pct_chg(pcr_days_df):
    """
    用pcr的指标和指数下一天的收益做相关性分析；
    :param pcr_days_df:
    :return:
    """
    #holding_period = 1
    # result_file = '.\\option_strategy\\result\\3d_profit.txt'
    # f = open(result_file, 'wb')
    limit_num_arr = np.array(range(4, 21)) / 10
    index_name = 'position_pcr'
    mean_pct_dict = defaultdict()
    pct_one_dict = defaultdict()
    occur_num_dict = defaultdict()
    for holding_period in range(1, 31):
        pcr_days_df['holding_profit'] = (pcr_days_df['50_index'].shift(-1 * holding_period) / pcr_days_df['50_index'] - 1) * 100
        for limit_num in limit_num_arr:
            down_pcr_days_df = pcr_days_df[pcr_days_df[index_name] < limit_num]
            mean_pct_chg = down_pcr_days_df['holding_profit'].mean()
            occur_num_dict[limit_num] = len(down_pcr_days_df)
            mean_pct_dict[limit_num, holding_period] = mean_pct_chg
            if holding_period == 1:
                pct_one_dict[limit_num] = mean_pct_chg
    pct_one_series = Series(pct_one_dict)
    pct_one_series.plot()
    return mean_pct_dict


def plot_heatmap_parameter(mean_pct_dict):
    """
    绘制平均收益关于limit_num和holding_period的参数的相关收益
    :param mean_pct_dict:
    :return:
    """
    res_df = pd.DataFrame(mean_pct_dict, index=[0]).T.reset_index()
    res_df.columns = ['N', 'M', 'return']
    res_mat = res_df.set_index(['N', 'M'])['return'].unstack()
    res_mat = res_mat.T
    cmap = sns.color_palette("RdBu_r", 40)
    fig = plt.figure(figsize=(12, 8))
    ax2 = plt.subplot(111)
    sns.heatmap(res_mat, yticklabels=True, annot=True, cmap=cmap, linecolor='black', linewidths=0.05, ax=ax2, cbar=True)
    # ax2.set_title(ths_time)
    plt.yticks(rotation=0)


def print_pcr_out(pcr_days_dict):
    out_file_name = '.\\option_strategy\\result\\pcr_result.txt'
    f = open(out_file_name, 'wb')
    f.write('trading_day,position_pcr,amount_pcr,volume_pcr\n')
    for trading_day, result_pcr in pcr_days_dict.items():
        str_line = trading_day + ',' + str(result_pcr[0]) + ',' + str(result_pcr[1]) + ',' + str(result_pcr[2]) + '\n'
        f.write(str_line)
    f.close()


if __name__ == '__main__':
    start_date = '2015-06-01'
    end_date = '2018-10-25'
    pcr_days_dict = calc_trading_days_pcr(start_date, end_date)
    print_pcr_out(pcr_days_dict)


