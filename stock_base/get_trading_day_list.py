# -*- coding: utf-8 -*-
"""

根据数据库的文件更新每天的日期文件夹

Thu 2018/03/15

@author: Tracy Zhu
"""

# 导入系统库
import sys
from WindPy import w

# 导入用户库
sys.path.append("..")
from stock_base.stock_data_api import *

trading_day_list_file_name =  "F:\\tool\\base_data\\Trading_Day.txt"
trading_day_list_file = open(trading_day_list_file_name, "w")

start_date = '2008-01-01'
trading_date = datetime.now()
end_date = trading_date.strftime('%Y-%m-%d')

w.start()

# index_df = get_index_data('000300.SH', start_date, end_date)
data = w.tdays(start_date, end_date)
trading_day_list = data.Times

for trading_day in trading_day_list:
    trading_day = trading_day.strftime("%Y%m%d")
    print trading_day
    print>>trading_day_list_file, trading_day

trading_day_list_file.close()