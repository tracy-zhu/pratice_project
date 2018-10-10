# -*- coding: utf-8 -*-
"""

# 对根据龙头股效应筛选出来的结果文件进行转化，结果未见是日调仓，改为周调仓，或者月调仓；

Fri 2018/08/13

@author: Tracy Zhu
"""

# 导入系统库
import sys

# 导入用户库
sys.path.append("..")
from stock_industry_analysis.volume_up_industry import *
from stock_base.stock_industry_base import *

result_file_name = "..\\stock_industry_analysis\\result\\back_test\\position_back_test_level1.csv"
out_file_name = "..\\stock_industry_analysis\\result\\back_test\\position_back_test_resample.csv"


def transfer_result_file(frequency):
    """
    将之前根据龙头股策略生成的日线调仓的行业板块降维到某一天调仓
    :param freq:'W-FRI', 'W-MON'
    :return:
    """
    global result_file_name, out_file_name
    f = open(out_file_name, 'wb')
    f.write(',time,position,code\n')
    stamp_index = []
    result_df = pd.read_csv(result_file_name, index_col= 0)
    for trading_day in result_df.time:
        stamp = datetime.strptime(trading_day, '%Y-%m-%d')
        stamp_index.append(stamp)
    DF_data = DataFrame(result_df.values, index=stamp_index, columns=result_df.columns)
    ts_series = pd.date_range('2017-01-01', '2018-08-08', freq=frequency)
    count_num = 0
    i = 0
    for trading_date in DF_data.index.unique():
        if trading_date >= ts_series[0] and i <= len(ts_series) - 2:
            if ts_series[i] <= trading_date < ts_series[i + 1]:
                position_df = DF_data[DF_data.index == ts_series[i]]
                if len(position_df) > 0:
                    for index in range(5):
                        position = position_df.position.values[index]
                        code = position_df.code.values[index]
                        day_str = trading_date.strftime('%Y-%m-%d')
                        str_line = str(count_num) + ',' + day_str + ',' + str(position) + ',' + code + '\n'
                        f.write(str_line)
                        count_num += 1
            else:
                i += 1
                position_df = DF_data[DF_data.index == ts_series[i]]
                if len(position_df) > 0:
                    for index in range(5):
                        position = position_df.position.values[index]
                        code = position_df.code.values[index]
                        day_str = trading_date.strftime('%Y-%m-%d')
                        print day_str
                        str_line = str(count_num) + ',' + day_str + ',' + str(position) + ',' + code + '\n'
                        f.write(str_line)
                        count_num += 1
    f.close()


if __name__ == '__main__':
    frequency = 'W-FRI'
    transfer_result_file(frequency)
