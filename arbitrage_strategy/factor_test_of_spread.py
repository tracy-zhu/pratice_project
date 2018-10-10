# -*- coding: utf-8 -*-
"""

# 本脚本用于测试能够应用到价差上不同因子的表现

Tue 2017/10/31

@author: Tracy Zhu
"""
# 导入系统库
import sys
import talib as ta

# 导入用户库：
sys.path.append("..")
from arbitrage_strategy.contract_spread_30min import *
from markt_maker.high_frequency_data_pattern_analysis import *


def load_spread_arr(instrument_id_1, instrument_id_2, frequency):
    data_file = "..\\arbitrage_strategy\\result\\" + instrument_id_1 + " & " + instrument_id_2 \
                + frequency + "_spread_arr.txt"
    spread_arr = np.loadtxt(data_file)
    spread_arr_diff = np.diff(spread_arr)
    # fig, ax = plt.subplots()
    # ax.plot(spread_arr_diff)
    return spread_arr, spread_arr_diff


def momentum_factor_generation(back_period, limit_change, spread_arr):
    spread_series = Series(spread_arr)
    spread_change = spread_series.diff(back_period)
    info_list = []
    for change_value in spread_change:
        if change_value > limit_change:
            info_list.append(1)
        elif change_value < -limit_change:
            info_list.append(-1)
        else:
            info_list.append(0)
    info_arr = np.array(info_list)
    return info_arr


def vix_factor_generation(back_period, spread_arr):
    spread_series = Series(spread_arr)
    spread_yield = spread_series.diff() #/ spread_series
    spread_yield_arr = np.array(spread_yield)
    std_list = [np.nan] * 10
    for i in range(len(spread_yield_arr) - back_period):
        std_value = np.std(spread_yield_arr[i:(i+back_period)])
        std_list.append(std_value)
    std_arr = np.array(std_list)
    return std_arr


def term_structure_factor_generation(back_period, spread_arr):
    pass


def basis_momentum_factor_generation(instrument_id_1, instrument_id_2, frequency, back_period, start_date, end_date):
    last_price_arr_1 = get_last_price_days(instrument_id_1, start_date, end_date, frequency)
    last_price_arr_2 = get_last_price_days(instrument_id_2, start_date, end_date, frequency)
    last_price_series_1 = Series(last_price_arr_1)
    cum_yield_series_1 = last_price_series_1.diff(back_period) / last_price_series_1
    last_price_series_2 = Series(last_price_arr_2)
    cum_yield_series_2 = last_price_series_2.diff(back_period) / last_price_series_2
    basis_momentum_arr = np.array(cum_yield_series_1 - cum_yield_series_2)
    basis_momentum_series = Series(basis_momentum_arr)
    spread_series = last_price_series_1 - last_price_series_2
    pfe_arr = get_pfe_arr(spread_series, back_period)
    pfe_series = Series(pfe_arr)
    data_frame = pd.concat([basis_momentum_series, spread_series, pfe_series], axis=1)
    csv_file_name = "..\\arbitrage_strategy\\result\\basis_momentum_series_01&05_30min.csv"
    data_frame.to_csv(csv_file_name)
    spread_arr = np.array(spread_series)
    return basis_momentum_arr, spread_arr


def back_period_optimistic(last_price_series_1, last_price_series_2, back_period):
    cum_yield_series_1 = last_price_series_1.diff(back_period) / last_price_series_1
    cum_yield_series_2 = last_price_series_2.diff(back_period) / last_price_series_2
    basis_momentum_arr = cum_yield_series_1 - cum_yield_series_2
    basis_momentum_series = Series(basis_momentum_arr)
    spread_series = last_price_series_1 - last_price_series_2
    spread_arr = np.array(spread_series)
    path_name = ".\\arbitrage_strategy\\picture\\basis_momentum_factor\\"
    figure_name = str(back_period) + "_.png"
    out_file_name = path_name + figure_name
    fig, ax1 = plt.subplots()
    fig.set_size_inches(23.2, 14.0)
    ax1.plot(spread_arr, color='b')
    ax2 = ax1.twinx()
    ax2.plot(basis_momentum_arr, color='r')
    ax1.set_title(figure_name)
    plt.savefig(out_file_name)


def factor_peformance(hold_period, info_arr, spread_arr):
    position = 0
    direction = 0
    hold_time = -1
    open_price = 0
    profit_list = []
    for index in range(len(info_arr)):
        info = info_arr[index]
        if hold_time != -1:
            hold_time += 1
        if position == 0:
            if info == 1:
                hold_time = 0
                position = 1
                direction = 1
                open_price = spread_arr[index]
            elif info == -1:
                direction = -1
                hold_time = 0
                position = -1
                open_price = spread_arr[index]
        else:
            if direction == 1 and hold_time >= hold_period:
                profit = spread_arr[index] - open_price
                profit_list.append(profit)
                hold_time = -1
                position = 0
            elif direction == -1 and hold_time >= hold_period:
                profit = open_price - spread_arr[index]
                profit_list.append(profit)
                hold_time = -1
                position = 0
    profit_series = Series(profit_list)
    total_profit = profit_series.sum()
    return total_profit


def factor_peformance_without_hold(spread_arr, info_arr):
    position = 0
    direction = 0
    hold_time = -1
    open_price = 0
    profit_list = []
    for index in range(len(info_arr)):
        info = info_arr[index]
        if hold_time != -1:
            hold_time += 1
        if position == 0:
            if info == 1:
                hold_time = 0
                position = 1
                direction = 1
                open_price = spread_arr[index]
            elif info == -1:
                direction = -1
                hold_time = 0
                position = -1
                open_price = spread_arr[index]
        else:
            if direction == 1 and info == -1:
                profit = spread_arr[index] - open_price
                profit_list.append(profit)
                hold_time = -1
                position = 0
            elif direction == -1 and info == 1:
                profit = open_price - spread_arr[index]
                profit_list.append(profit)
                hold_time = -1
                position = 0
    profit_series = Series(profit_list)
    total_profit = profit_series.sum()
    return total_profit


def figure_demonstration(spread_arr, info_arr):
    fig,  (ax0, ax1) = plt.subplots(nrows=2, ncols=1, figsize=(23.2, 14.0))
    ax0.plot(spread_arr, label='spread_arr', color='b')
    ax1.plot(info_arr, label='info_arr', color='r')
    ax0.legend('upper left')
    ax1.legend('upper left')


def main():
    instrument_id_1 = "RB1710"
    instrument_id_2 = 'RB1801'
    frequency = '15min'
    result_file_name = "..\\arbitrage_strategy\\result\\momentum_factor_test_" + instrument_id_1 + " & " + instrument_id_2 \
                + frequency + "_spread_arr.txt"
    result_file = open(result_file_name, 'wb')
    spread_arr, _ = load_spread_arr(instrument_id_1, instrument_id_2, frequency)
    for limit_change in range(10):
        for back_period in range(1, 90):
            for hold_period in range(1, 90):
                print back_period, hold_period
                info_arr = momentum_factor_generation(back_period, limit_change, spread_arr)
                total_profit = factor_peformance(hold_period, info_arr, spread_arr)
                str_line = str(back_period) + "," + str(hold_period) + ',' + str(limit_change) + "," + str(total_profit) + '\n'
                result_file.write(str_line)
    result_file.close()


def basis_momentum_factor_peformance(spread_arr, basis_momentum_arr):
    position = 0
    direction = 0
    open_price = 0
    profit_list = []
    open_level_1 = 0.004
    # 1代表已经具备平仓机会，等待下个信号确认平仓， 0代表尚未有平仓机会
    for index in range(len(basis_momentum_arr)):
        info = basis_momentum_arr[index]
        if position == 0:
            if info <= -open_level_1 :
                position = 1
                direction = 1
                open_price = spread_arr[index]
            elif info >= open_level_1:
                direction = -1
                position = 1
                open_price = spread_arr[index]
        else:
            if direction == 1 and info >= open_level_1:
                profit = spread_arr[index] - open_price
                profit_list.append(profit)
                position = 0
            elif direction == -1 and info <= -open_level_1:
                profit = open_price - spread_arr[index]
                profit_list.append(profit)
                position = 0
    profit_series = Series(profit_list)
    total_profit = profit_series.sum()
    cum_profit_series = profit_series.cumsum()
    print total_profit
    cum_profit_series.plot()
    return total_profit, cum_profit_series


def basis_momentum_factor_plot(instrument_id_1, instrument_id_2, frequency, back_period):
    datetime_now = datetime.now()
    index_day = datetime_now - timedelta(days=14)
    start_date = index_day.strftime('%Y%m%d')
    end_date = datetime_now.strftime("%Y%m%d")
    basis_momentum_arr, spread_arr = \
        basis_momentum_factor_generation(instrument_id_1, instrument_id_2, frequency, back_period, start_date, end_date)
    fig, ax1 = plt.subplots()
    path_name = "..\\demonstration\\basis_momentum_factor_plot.png"
    fig.set_size_inches(23.2, 14.0)
    ax1.plot(spread_arr, color='b')
    ax2 = ax1.twinx()
    ax2.plot(basis_momentum_arr, color='r')
    plt.savefig(path_name)


if __name__ == '__main__':
    instrument_id_1 = "RB1801"
    instrument_id_2 = 'RB1805'
    frequency = '30min'
    back_period = 40
    basis_momentum_factor_plot(instrument_id_1, instrument_id_2, frequency, back_period)

