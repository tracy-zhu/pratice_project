# -*- coding: utf-8 -*-
"""

# 选择用RSI，收盘价低于20日均线15%，当日涨跌幅大于4%， 当日的成交量创近20日新低；

# 选出的股票持有7天观察收益率；

# 尝试将选股策略总结成一个模板；

Fri 2018/07/31

@author: Tracy Zhu
"""

# 导入系统库
import sys

# 导入用户库
sys.path.append("..")
from stock_base.stock_backtest_function import *
import talib as ta
out_file_folder = '..\\techiniacl_analysis_stock\\result\\'

def calc_rsi(price_series, N):
    """
    N取6
    :param price_series:
    :param N:
    :return:
    """
    rsi_array = ta.RSI(np.array(price_series), N)
    rsi_series = Series(rsi_array, index=price_series.index)
    return rsi_series


def calc_deviation_ma(price_series, ma_num):
    """
    计算当日收盘价相对于15日均线的偏离度
    :param price_series: 收盘价序列
    :param ma_num:
    :return:
    """
    ma_price_series = pd.rolling_mean(price_series, ma_num)
    close_deviation = (price_series - ma_price_series) / ma_price_series
    return close_deviation



def get_calc_df(start_date, end_date):
    """
    根据上面的函数，计算出包含指标列的df
    :param start_date:
    :param end_date:
    :return:
    """
    sql = 'SELECT * FROM stock_db.daily_price_tb WHERE time  >= \"{start_date}\" AND time ' \
          ' <=  \"{end_date}\"'.format(start_date=start_date, end_date=end_date)
    tp_table = fetchall_sql(sql)
    data_df = pd.DataFrame(list(tp_table))
    data_df.columns = retrieve_column_name('stock_db', 'daily_price_tb')
    data_df.VOLUME = data_df.VOLUME.replace(0, np.nan)
    data_df = data_df[data_df.VOLUME > 0]


    data_df['rsi'] = data_df.groupby('code')['CLOSE'].apply(lambda x, N=6: calc_rsi(x, N))
    data_df['close_deviation'] = data_df.groupby('code')['CLOSE'].apply(lambda x,ma_num=20:calc_deviation_ma(x, ma_num))
    data_df['min_volume'] = data_df.groupby('code')['VOLUME'].apply(lambda x: x.rolling(window=20).min())
    data_df['is_min'] = (data_df['VOLUME'] <= data_df['min_volume'])
    data_df = data_df[data_df['PCT_CHG'] >= 4]
    select_df = data_df[data_df['rsi'] < 20]
    # select_df = select_df[select_df['is_min'] == True]
    select_df = select_df[select_df['close_deviation'] <= -1 * 0.15]
    return select_df


def get_all_calc_df(start_date, end_date):
    """
    内存原因，分成每一段计算
    :param start_date:
    :param end_date:
    :return:
    """
    indicator_df = DataFrame()
    collect_dict = defaultdict()
    key_num = 0
    step_num = 150
    trading_day_list = get_trading_day_list()
    model_date_list = []
    for j in trading_day_list:
        trading_day = change_trading_day_format(j[:-1])
        if trading_day >= start_date:
            model_date_list.append(trading_day)
    begin_step = 0
    end_step = begin_step + step_num
    end_time = 0
    while end_time != end_date:
        begin_time = model_date_list[begin_step]
        if end_step >= len(model_date_list) - 1:
            end_step = len(model_date_list) - 1
        end_time = model_date_list[end_step]
        print(end_time)
        begin_step = end_step + 1
        end_step = begin_step + step_num
        temp_df = get_calc_df(begin_time, end_time)
        if len(temp_df) > 0:
            collect_dict[key_num] = temp_df
            key_num += 1
    for keys, temp_df in collect_dict.items():
        indicator_df = pd.concat([indicator_df, temp_df], axis=0)
    select_file_name = out_file_folder + "select_df.csv"
    indicator_df.to_csv(select_file_name)
    return indicator_df


def print_holding_profit_out(select_file_name):
    indicator_df = pd.read_csv(select_file_name)
    select_df = indicator_df[indicator_df["is_min"]==False]
    select_df = select_df[select_df["PCT_CHG"] <= 9.5]
    # select_df = indicator_df
    profit_file_name = out_file_folder + 'rsi_strategy_test.csv'
    with open(profit_file_name, 'wb') as f:
        f.write('stock_code,trading_day,holding_profit\n')
        for index,row in select_df.iterrows():
            stock_code = row.code
            trading_day = row.time
            profit = stock_holding_profit(stock_code, trading_day, holding_period=7)
            str_line = stock_code + ',' + trading_day + ',' + str(profit) + '\n'
            f.write(str_line)


def profit_analysis(profit_file_name):
    profit_df = pd.read_csv(profit_file_name)
    holding_profit = profit_df.holding_profit
    win_ratio = float(sum(holding_profit > 1)) / float(len(holding_profit))
    print "average holding profit is " + str(holding_profit.mean())
    print "win ratio is " + str(win_ratio)
    holding_profit.hist()


if __name__ == '__main__':
    start_date = '2013-01-01'
    end_date = '2018-09-06'