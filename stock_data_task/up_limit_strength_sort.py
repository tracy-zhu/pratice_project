# -*- coding: utf-8 -*-
"""

# 对当天所有涨停的股票按涨停时间，是否被打开，封单量比，成交量比等参数确定涨停板强度并进行排序；

# 每日生成一个文件

Thu 2018/03/15

@author: Tracy Zhu
"""

# 导入系统库
import sys

# 导入用户库
sys.path.append("..")
from stock_tool.find_defensive_stock import *

out_file_folder = "D:\\strategy\\open_price_strategy\\stock_data\\"

now = datetime.now()
trading_day = now.strftime('%Y-%m-%d')
# trading_day = '2018-03-16'
day_folder = out_file_folder + trading_day + "\\"

isExists = os.path.exists(day_folder)
if not isExists:
    os.makedirs(day_folder)

stock_up_limit_list = find_stock_up_limit(trading_day, 1)


def sort_stock_by_up_time(stock_code_list, trading_day):
    """
    根据涨停时间的先后，对当天涨停的股票进行排序；
    :param stock_code_list:
    :return:
    """
    stock_up_limit_always_dict = defaultdict()
    stock_up_limit_not_dict = defaultdict()
    for stock_code in stock_code_list:
        first_up_limit_time, is_always_up_limit = find_stock_up_limit_time_from_raw_data(stock_code, trading_day)
        if is_always_up_limit == 1:
            stock_up_limit_always_dict[stock_code] = first_up_limit_time
        else:
            stock_up_limit_not_dict[stock_code] = first_up_limit_time
    sorted_always_dict = sorted(stock_up_limit_always_dict.items(), key=lambda d: d[1])
    sorted_not_always_dict = sorted(stock_up_limit_not_dict.items(), key=lambda d: d[1])
    return sorted_always_dict, sorted_not_always_dict


def get_stock_up_limit_strength(stock_code, trading_day):
    """
    在find_stock_up_limit_time_from_raw_data中，确定的股票涨停时间和后面是否打开
    这个函数主要是涨停板的封板强度；
    主要是封板的时间比例；
    :param stock_code:
    :param trading_day:
    :return:
    """
    up_limit_ratio = 0
    file_name = stock_code.split('.')[0] + "_" + stock_code.split('.')[1] + '_' + trading_day + '.csv'
    data_file_name = stock_minute_file_path + file_name
    try:
        df_table = pd.read_csv(data_file_name)
    except:
        print "there is no file name " + file_name
    else:
        start_time = trading_day + ' 09:30'
        df_table.index = df_table.time
        high_price_series = df_table.high
        high_price_series = high_price_series.dropna()
        high_price_series = high_price_series[high_price_series.index > start_time]
        up_limit_price = high_price_series.max()
        up_limit_series = high_price_series[high_price_series >= up_limit_price]
        first_up_limit_time = up_limit_series.index[0]
        high_series_after_first_limit = high_price_series[high_price_series.index >= first_up_limit_time]
        up_limit_ratio = float(len(high_series_after_first_limit)) / float(len(high_price_series))
    return up_limit_ratio


def find_continuous_up_limit_days(stock_code, trading_day):
    """
    找出算上今天涨停板，该股票最近连续涨停的天数
    :param stock_code:
    :param trading_day:
    :return:
    """
    continuous_days = 0
    end_date = trading_day
    start_date = get_next_trading_day_stock(trading_day, -15)
    sql_sentence = 'SELECT * FROM stock_db.stock_trade_status_tb where time >= \"{start_date}\" and time <= \"{end_date}\" and code = \"{stock_code}\"'\
        .format(start_date=start_date, end_date=end_date, stock_code=stock_code)
    tp_table = fetchall_sql(sql_sentence)
    df_table = pd.DataFrame(list(tp_table), columns=['time', 'code', 'maxupordown', 'trade_status', 'susp+days', 'susp_reason'])
    maxupordown_list = list(df_table.maxupordown)
    for if_up_limit in maxupordown_list[::-1]:
        if if_up_limit == 1:
            continuous_days += 1
        else:
            break
    return continuous_days


def find_ths_concept_name(stock_code, trading_day):
    """
    在stock_data里面有生成概念列表的函数，将概念列表结果转化为成str
    :param stock_code:
    :param trading_day:
    :return:
    """
    chi_name_list = []
    concept_list = find_stock_concept_ifind(stock_code, trading_day)
    for values in concept_list:
        chi_name_list.append(values.split(',')[-1])
    concept_name_str = ';'.join(chi_name_list)
    return concept_name_str


sorted_always_dict, sorted_not_always_dict = sort_stock_by_up_time(stock_up_limit_list, trading_day)

for values in sorted_always_dict:
    stock_code = values[0]
    up_limit_time = values[1].split(' ')[-1]
    concept_name_str = find_ths_concept_name(stock_code, trading_day)
    chi_name = find_stock_chi_name(stock_code)
    up_limit_ratio = get_stock_up_limit_strength(stock_code, trading_day)
    continuous_days = find_continuous_up_limit_days(stock_code, trading_day)
    str_line = stock_code + ',' + chi_name + ',' + up_limit_time + ',' + str(up_limit_ratio) + ',' + str(continuous_days) + ',' + concept_name_str
    print str_line