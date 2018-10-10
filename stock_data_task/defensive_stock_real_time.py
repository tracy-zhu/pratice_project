# -*- coding: utf-8 -*-
"""

# 生成日内某段时间股票的涨幅排名

# 在大盘下跌的过程中显得比较重要

# 跟之前不同的是，读的是钱哥实时行情的数据

Thu 2018/03/26

@author: Tracy Zhu
"""

# 导入系统库
import sys

# 导入用户库
sys.path.append("..")
from stock_base.stock_file_api import *
from stock_base.stock_data_api import *

now = datetime.now()
trading_day = now.strftime('%Y-%m-%d')

begin_time = 103400
end_time = 131400

begin_slice_df = read_real_time_stock_data_wind(trading_day, begin_time)
end_slice_df = read_real_time_stock_data_wind(trading_day, end_time)


stock_code_yield_dict = defaultdict()
stock_code_list = begin_slice_df['index_code']

for stock_code in stock_code_list:
    print stock_code
    begin_stock_data = get_stock_slice_data(stock_code, begin_slice_df)
    end_stock_data = get_stock_slice_data(stock_code, end_slice_df)
    pct_chg = end_stock_data.pct_chg.values[0] - begin_stock_data.pct_chg.values[0]
    stock_code_yield_dict[stock_code] = pct_chg


sorted_dict = sorted(stock_code_yield_dict.items(), key=lambda d: d[1], reverse=True)


for values in sorted_dict[:20]:
    stock_code = values[0]
    chi_name = find_stock_chi_name(stock_code)
    stock_yield = values[1]
    print stock_code, ',', chi_name, ',', stock_yield