# -*- coding: utf-8 -*-
"""

# 用于统计期权交割日有没有卖空的无风险套利机会

# 50ETF期权的上市日期为2015年2月9日

Tue 2018/03/02

@author: Tracy Zhu
"""

# 导入系统库
import sys
from WindPy import w

# 导入用户库
sys.path.append("..")
from python_base.plot_method import *

option_exercise_instrument_dict = defaultdict(list)

file_name = "..\\option_strategy\\all_option_data.csv"
option_info_df = pd.read_csv(file_name)
out_file_name = "..\\option_strategy\\expire_data_market.csv"
f = open(out_file_name, 'wb')
f.write('expire_date, option_name, open_price, high_price, close_price, etf_open, etf_high, etf_low, etf_close\n')


def download_data_wind(start_date, end_date, var_list):
    if w.isconnected() == False:
        w.start()
    raw = w.wsd(var_list, "open, high, low, close",start_date, end_date, "")
    raw_df = pd.DataFrame(raw.Data, index=raw.Fields, columns=raw.Times)
    raw_df = raw_df.T
    return raw_df


for index in option_info_df.index[:-1]:
    one_line = option_info_df.loc[index]
    wind_code = str(int(one_line["wind_code"])) + ".SH"
    trade_code = one_line["trade_code"]
    expire_date = one_line['expire_date'].replace('/', '-')
    option_exercise_instrument_dict[expire_date].append((wind_code, trade_code))


for exercise_date, wind_code_list in option_exercise_instrument_dict.items():
    exercise_datetime = datetime.strptime(exercise_date, '%Y-%m-%d')
    if exercise_datetime < datetime.now():
        for code_tuple in wind_code_list:
            wind_code = code_tuple[0]
            option_name = code_tuple[1]
            print exercise_date, option_name
            option_data = download_data_wind(exercise_date, exercise_date, wind_code)
            etf_data = download_data_wind(exercise_date, exercise_date, "510050.SH")
            if len(option_data) > 0 and len(etf_data) > 0:
                try:
                    close_price = option_data.CLOSE.values[0]
                    open_price = option_data.OPEN.values[0]
                    high_price = option_data.HIGH.values[0]
                    etf_close = etf_data.CLOSE.values[0]
                    etf_open = etf_data.OPEN.values[0]
                    etf_high = etf_data.HIGH.values[0]
                    etf_low = etf_data.LOW.values[0]
                except:
                    print "data is wrong!"
                else:
                    if close_price < 0.001 and high_price > 0.001:
                        str_line = exercise_date + ',' + option_name + ',' + str(open_price) + ','\
                                   + str(high_price) + ',' + str(close_price) + ',' + str(etf_open) + ','\
                                   + str(etf_high) + ',' + str(etf_low) + ',' + str(etf_close) + '\n'
                        f.write(str_line)

f.close()
