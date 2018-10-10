# -*- coding: utf-8 -*-
"""

# 本脚本研究降维之后的价差序列，降维时间有15分钟，30分钟，60分钟

Tue 2017/10/24

@author: Tracy Zhu
"""
# 导入系统库
import sys
import talib as ta

# 导入用户库：
sys.path.append("..")
from python_base.plot_method import *
trading_day_list = get_trading_day_list()


def get_low_dimension_data(instrument_id, trading_day, frequency):
    quote_data = read_data(instrument_id, trading_day)
    open_index = quote_data.index[0]
    quote_data = quote_data[quote_data.index > open_index]
    end_index = quote_data[quote_data.Update_Time <= "15:00:00"].index[-1]
    quote_data = quote_data[quote_data.index <= end_index]
    resample_data = get_dataframe(quote_data, frequency)
    return resample_data


def get_day_contract_spread(instrument_id_1, instrument_id_2, trading_day, frequency):
    """
    获取降维后两个合约的最新价的价差序列
    :param instrument_id_1:
    :param instrument_id_2:
    :param trading_day:
    :param frequency: 降维频率15min, 30min, 60min
    :return: 返回价差序列
    """
    resample_data1 = get_low_dimension_data(instrument_id_1, trading_day, frequency)
    resample_data2 = get_low_dimension_data(instrument_id_2, trading_day, frequency)
    contract_spread = resample_data1.Last_Price - resample_data2.Last_Price
    spread_list = list(contract_spread)
    return spread_list


def get_day_contract_series_spread(instrument_id_1, instrument_id_2, trading_day, frequency):
    """
    获取降维后两个合约的最新价的价差序列
    :param instrument_id_1:
    :param instrument_id_2:
    :param trading_day:
    :param frequency: 降维频率15min, 30min, 60min
    :return: 返回价差序列, 与前面不同， 这个series是代index的, index
    """
    resample_data1 = get_low_dimension_data(instrument_id_1, trading_day, frequency)
    resample_data2 = get_low_dimension_data(instrument_id_2, trading_day, frequency)
    contract_spread = resample_data1.Last_Price - resample_data2.Last_Price
    index_list = []
    for index in contract_spread.index:
        new_index = trading_day[-4:] + str(index.hour).zfill(2) + str(index.minute).zfill(2)
        print new_index
        index_list.append(new_index)
    contract_spread_series = Series(contract_spread.values, index=index_list)
    return contract_spread_series


def get_butterfly_spread_series(instrument_id_1, instrument_id_2, instrument_id_3, trading_day, frequency):
    """
    获取降维后三个合约的最新价的蝶式价差序列
    :param instrument_id_1: RB1801
    :param instrument_id_2: RB1805
    :param instrument_id_3: RB1810
    :param trading_day:
    :param frequency: 降维频率15min, 30min, 60min
    :return: 返回价差序列, 与前面不同， 这个series是代index的, index
    """
    resample_data1 = get_low_dimension_data(instrument_id_1, trading_day, frequency)
    resample_data2 = get_low_dimension_data(instrument_id_2, trading_day, frequency)
    resample_data3 = get_low_dimension_data(instrument_id_3, trading_day, frequency)
    contract_spread = resample_data1.Last_Price + resample_data3.Last_Price - 2 * resample_data2.Last_Price
    index_list = []
    for index in contract_spread.index:
        new_index = trading_day[-4:] + str(index.hour).zfill(2) + str(index.minute).zfill(2)
        print new_index
        index_list.append(new_index)
    butterfly_spread_series = Series(contract_spread.values, index=index_list)
    return butterfly_spread_series


def get_last_price_days(instrument_id, start_date, end_date, frequency):
    total_spread_list = []
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        if start_date <= trading_day <= end_date:
            print trading_day
            resample_data = get_low_dimension_data(instrument_id, trading_day, frequency)
            spread_list = list(resample_data.Last_Price)
            total_spread_list.extend(spread_list)
    last_price_arr = np.array(total_spread_list)
    return last_price_arr


def get_contract_spread_days(instrument_id_1, instrument_id_2, start_date, end_date, frequency):
    total_spread_list = []
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        if start_date <= trading_day <= end_date:
            print trading_day
            spread_list = get_day_contract_spread(instrument_id_1, instrument_id_2, trading_day, frequency)
            total_spread_list.extend(spread_list)
    total_spread_arr = np.array(total_spread_list)
    return total_spread_arr


def get_contract_spread_series_days(instrument_id_1, instrument_id_2, start_date, end_date, frequency):
    total_spread_series = get_day_contract_series_spread(instrument_id_1, instrument_id_2, start_date, frequency)
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        if start_date < trading_day <= end_date:
            print trading_day
            contract_spread_series = get_day_contract_series_spread(instrument_id_1, instrument_id_2, trading_day, frequency)
            total_spread_series = pd.concat([total_spread_series, contract_spread_series])
    return total_spread_series


def get_butterfly_spread_series_days(instrument_id_1, instrument_id_2, instrument_id_3, start_date, end_date, frequency):
    total_spread_series = get_butterfly_spread_series(instrument_id_1, instrument_id_2, instrument_id_3, start_date, frequency)
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        if start_date < trading_day <= end_date:
            print trading_day
            contract_spread_series = get_butterfly_spread_series(instrument_id_1, instrument_id_2, instrument_id_3, trading_day, frequency)
            total_spread_series = pd.concat([total_spread_series, contract_spread_series])
    return total_spread_series


def load_spread_arr(instrument_id_1, instrument_id_2, frequency):
    frequency = '15min'
    data_file = "..\\arbitrage_strategy\\result\\" + instrument_id_1 + " & " + instrument_id_2\
                + frequency + "_spread_arr.txt"
    spread_arr = np.loadtxt(data_file)
    spread_arr_diff = np.diff(spread_arr)
    fig, ax = plt.subplots()
    ax.plot(spread_arr_diff)
    return spread_arr, spread_arr_diff


def get_run_num(spread_arr_diff):
    """
    函数用来检验价差差分序列的游程，分别返回的是游程的个数,以及每个游程的长度
    单独一个不构成游程，大于等于2个正负号一样们才算一个游程
    :param spread_arr_diff: 价差的一阶差分序列
    :return: run_num 游程个数, run_series: 游程列表, 每个游程的连续次数
    """
    spread_arr_diff_run = spread_arr_diff[1:] * spread_arr_diff[:-1]
    run_num = 0
    run_list = []
    run_length = 1
    for run_test in spread_arr_diff_run:
        if run_test > 0:
            if run_length == 1:
                run_num += 1
                run_length += 1
            else:
                run_length += 1
        if run_test < 0:
            if run_length != 1:
                run_list.append(run_length)
                run_length = 1
    run_series = Series(run_list)
    return run_num, run_series


def get_advance_run_num(spread_arr_diff, spread_arr, percent, draw_down_tick, flag):
    """
    上一个函数的游程检验中，只要前后的正负号不同，就代表一个游程结束，
    这里做一个改进有两种方法，一个是按照之前游程累计和回撤的百分比以内都算一个游程
    另外一个是按照回撤的绝对点数
    :param spread_arr_diff:
    :param spread_arr: 价差序列
    :param percent: 回撤的百分比
    :param draw_down_tick: 回撤的绝对点数
    :param flag: 0 代表以回撤的百分比计算游程， 1 代表用回撤的绝对点数计算流程
    :return: 游程个数 run_num , 游程距离列表： run_list
    """
    run_length = 0
    run_num = 0
    run_list = []
    run_distance = 0
    extreme_value = 0
    first_spread_change = 0
    start_spread = 0
    # direction buy is 1, sell is -1
    direction = 0
    if flag == 0:
        pass
    elif flag == 1:
        for i in range(len(spread_arr_diff)):
            spread_diff = spread_arr_diff[i]
            if run_distance == 0:
                run_distance = spread_diff
                extreme_value = spread_diff
                first_spread_change = spread_diff
                start_spread = spread_arr[i]
                run_length = 1
            elif run_distance > 0:
                direction = 1
                run_distance = run_distance + spread_diff
                run_length += 1
                extreme_value = run_distance if run_distance > extreme_value else extreme_value
                if run_distance < extreme_value - draw_down_tick:
                    run_distance = run_distance - first_spread_change
                    run_info = (run_distance, direction, first_spread_change, start_spread)
                    run_list.append(run_info)
                    run_distance = 0
                    if run_length > 2:
                        run_num += 1
                    run_length = 0
            elif run_distance < 0:
                direction = -1
                run_distance = run_distance + spread_diff
                run_length += 1
                extreme_value = run_distance if run_distance < extreme_value else extreme_value
                if run_distance > extreme_value + draw_down_tick:
                    run_distance = run_distance - first_spread_change
                    run_info = (run_distance, direction, first_spread_change, start_spread)
                    run_list.append(run_info)
                    run_distance = 0
                    if run_length > 2:
                        run_num += 1
                    run_length = 0
    return run_num, run_list


def get_cum_profit(run_list):
    total_profit = 0
    profit_list = []
    for run_info in run_list:
        total_profit = total_profit + run_info[0] * run_info[1]
        profit_list.append(total_profit)
    profit_series = Series(profit_list)
    profit_series.plot()


def stack_spread_arr(instrument_id_1, instrument_id_2, start_date, end_date, frequency):
    """
    将每个合约的价差换位日期加时间为行，年份为列的data_frame
    :param instrument_id_1:
    :param instrument_id_2:
    :param frequency: 15min, 30min, 60min
    :param start_date:格式为 m%d% 0517
    :param end_date: 格式同start_date, 1023
    :return:
    """
    year_list = ['2015', '2016', '2017']
    total_year_dict = defaultdict()
    for year in year_list:
        if instrument_id_1[-2:] == '01' and instrument_id_2[-2:] == '05':
            instrument_id_1_new = instrument_id_1[:2] + str(int(year[-2:]) + 1) +instrument_id_1[-2:]
            instrument_id_2_new = instrument_id_2[:2] + str(int(year[-2:]) + 1) +instrument_id_2[-2:]
            begin_date = year + start_date
            end_date_new = year + end_date
            spread_contract_series = get_contract_spread_series_days(instrument_id_1_new, instrument_id_2_new, begin_date, end_date_new, frequency)
            total_year_dict[year] = spread_contract_series
        if instrument_id_1[-2:] == '10' and instrument_id_2[-2:] == '01':
            instrument_id_1_new = instrument_id_1[:2] + str(int(year[-2:])) +instrument_id_1[-2:]
            instrument_id_2_new = instrument_id_2[:2] + str(int(year[-2:]) + 1) +instrument_id_2[-2:]
            begin_date = year + start_date
            end_date_new = year + end_date
            spread_contract_series = get_contract_spread_series_days(instrument_id_1_new, instrument_id_2_new, begin_date, end_date_new, frequency)
            total_year_dict[year] = spread_contract_series
        if instrument_id_1[-2:] == '05' and instrument_id_2[-2:] == '10':
            instrument_id_1_new = instrument_id_1[:2] + str(int(year[-2:]) + 1) +instrument_id_1[-2:]
            instrument_id_2_new = instrument_id_2[:2] + str(int(year[-2:]) + 1) +instrument_id_2[-2:]
            begin_date = year + start_date
            end_date_new = str(int(year) + 1) + end_date
            spread_contract_series = get_contract_spread_series_days(instrument_id_1_new, instrument_id_2_new, begin_date, end_date_new, frequency)
            total_year_dict[year] = spread_contract_series
    spread_data_frame = DataFrame(total_year_dict)
    if instrument_id_1[-2:] == '05' and instrument_id_2[-2:] == '10':
        first_spread_data_frame = spread_data_frame[spread_data_frame.index >= "10190000"]
        second_spread_data_frame = spread_data_frame[spread_data_frame.index < "10190000"]
        spread_data_frame = pd.concat([first_spread_data_frame, second_spread_data_frame])
    return spread_data_frame


def load_spead_data_frame(month_str_1, month_str_2, frequency):
    month_str_1 = '01'
    month_str_2 = '05'
    file_name = ".\\arbitrage_strategy\\result\\data_frame\\" + month_str_1 + " & " + month_str_2 + '_' \
                + frequency + "_spread_data_frame.csv"
    spread_data_frame = pd.read_csv(file_name, index_col=0)
    if month_str_1 == '05':
        spread_data_frame = spread_data_frame.dropna(how='any', subset=['2015', '2016'])
    elif month_str_1 == '01':
        first_spread_data_frame = spread_data_frame[spread_data_frame.index < 10270900]
        first_spread_data_frame = first_spread_data_frame.dropna(how='any')
        second_spread_data_frame = spread_data_frame[spread_data_frame.index >= 10270900]
        second_spread_data_frame = second_spread_data_frame.dropna(how='any', subset=['2015', '2016'])
        spread_data_frame = pd.concat([first_spread_data_frame, second_spread_data_frame])
    else:
        spread_data_frame = spread_data_frame.dropna(how="any")
    fig, ax = plt.subplots()
    fig.set_size_inches(23.2, 14.0)
    for column_names in spread_data_frame.columns:
        ax.plot(spread_data_frame[column_names].values, label=column_names)
        ax.legend(loc='best')
    path_name = "..\\arbitrage_strategy\\picture\\total_year\\"
    isExists = os.path.exists(path_name)
    if not isExists:
        os.makedirs(path_name)
    figure_name = "period_of_" + frequency + "_" + month_str_1 + "_" + month_str_2 + " from " \
                    +  ".png"
    out_file_name = path_name + figure_name
    ax.set_title(figure_name)
    plt.savefig(out_file_name)


def out_data_frame_to_csv(frequency_list, test_info):
    for test_group in test_info:
        instrument_id_1 = test_group[0]
        instrument_id_2 = test_group[1]
        start_date = test_group[2]
        end_date = test_group[3]
        for frequency in frequency_list:
            file_name = "..\\arbitrage_strategy\\result\\data_frame\\" + instrument_id_1[-2:] + " & " + instrument_id_2[-2:] + '_' \
                        + frequency + "_spread_data_frame.csv"
            spread_data_frame = stack_spread_arr(instrument_id_1, instrument_id_2, start_date, end_date, frequency)
            spread_data_frame.to_csv(file_name)


def output_spread_arr_to_txt():
    frequency_list = ['30min', '60min', '15min']
    instrument_id_1 = 'RB1510'
    instrument_id_2 = "RB1601"
    start_date = '20150119'
    end_date = '20150930'
    for frequency in frequency_list:
        file_name = "..\\arbitrage_strategy\\result\\data_frame\\" + instrument_id_1 + " & " + instrument_id_2 + "_" \
                    + frequency + "_spread_data_frame.csv"
        total_spread_arr = stack_spread_arr(instrument_id_1, instrument_id_2, start_date, end_date, frequency)
        np.savetxt(file_name, total_spread_arr)
        fig, ax = plt.subplots()
        fig.set_size_inches(23.2, 14.0)
        ax.plot(total_spread_arr)
        path_name = "..\\arbitrage_strategy\\picture\\"
        isExists = os.path.exists(path_name)
        if not isExists:
            os.makedirs(path_name)
        figure_name = "period_of_" + frequency + "_" + instrument_id_1 + "_" + instrument_id_2 + " from " \
                      + start_date + " to " + end_date + ".png"
        out_file_name = path_name + figure_name
        ax.set_title(figure_name)
        plt.savefig(out_file_name)


def output_butterfly_spread():
    instrument_list = ['RB1805', 'RB1801', 'RB1810']
    instrument_id_1 = instrument_list[0]
    instrument_id_2 = instrument_list[1]
    instrument_id_3 = instrument_list[2]
    start_date = '20171019'
    end_date = "20171031"
    frequency = "30min"
    total_butterfly_spread_series = get_butterfly_spread_series_days(instrument_id_1, instrument_id_2, instrument_id_3, start_date, end_date, frequency)
    csv_file = "..\\arbitrage_strategy\\result\\" + instrument_id_1 + " & " + instrument_id_2 + " & " + instrument_id_3\
                + frequency + "_butterfly_spread.csv"
    total_butterfly_spread_series.to_csv(csv_file)


if __name__ == '__main__':
    #frequency_list = ['30min', '60min', '15min']
    # frequency_list = ['30min']
    # test_info = [("RB1710", "RB1801", "0119", "0930"), ("RB1705", "RB1710", "1019", "0430"),
    #              ("RB1801", "RB1805", "0525", "1231")]
    # test_info = [("RB1801", "RB1805", "0525", "1231")]
    # out_data_frame_to_csv(frequency_list, test_info)
    instrument_id_1 = "RB1801"
    instrument_id_2 = "RB1805"
    frequency = "1min"
    start_date = "20170517"
    end_date = '20171206'
    spread_arr = get_contract_spread_days(instrument_id_1, instrument_id_2, start_date, end_date, frequency)
    plt.hist(spread_arr)
