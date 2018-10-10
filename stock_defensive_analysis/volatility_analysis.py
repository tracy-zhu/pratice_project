# -*- coding: utf-8 -*-
"""

# 计算大盘在最近震荡的一段时间内，能够稳步上升的股票

# 股市就按照沪深300来计算；

WED 2018/5/7

@author: Tracy Zhu
"""
# 导入系统库
import sys

# 导入用户库：
sys.path.append("..")
from stock_base.stock_volatility_generation import *

holding_days = 50
# now = datetime.now()
# end_date = now.strftime('%Y-%m-%d')
end_date = '2018-05-08'
start_date = '2018-03-20'
# start_date = get_next_trading_day_stock(end_date, -1 * holding_days)
index_code = "000300.SH"

all_stock_code_list = get_all_stock_code_list(start_date)

sorted_volatility_stock = volatility_sort(all_stock_code_list, end_date, holding_days)

for stock_code, volatility_value in sorted_volatility_stock[:20]:
    chi_name = find_stock_chi_name(stock_code)
    print stock_code, ',', chi_name, ',', volatility_value