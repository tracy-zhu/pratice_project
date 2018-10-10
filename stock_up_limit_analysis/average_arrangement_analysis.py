# -*- coding: utf-8 -*-
"""

# 筛选均线呈多头排列的股票

# 并且统计每条均线的距离

# 均线多头排列有明显的落后效应；

Tue 2018/7/18

@author: Tracy Zhu
"""
# 导入系统库
import sys
import math
import itertools
import scipy.stats as st

# 导入用户库：
sys.path.append("..")
from stock_base.stock_data_api import *
from datetime import date

start_date = "2018-04-01"
end_date = "2018-07-17"
# pre_3_date_str = get_next_trading_day_stock(end_date, -1)
pre_3_date_str = end_date
year = int(pre_3_date_str.split('-')[0])
month = int(pre_3_date_str.split('-')[1])
days = int(pre_3_date_str.split('-')[-1])
pre_3_date = date(year, month, days)

sql = 'SELECT * FROM stock_db.daily_price_tb WHERE time  >= \"{start_date}\" AND time ' \
      ' <=  \"{end_date}\"'.format(start_date=start_date, end_date=end_date)
tp_table = fetchall_sql(sql)
data_df = pd.DataFrame(list(tp_table))
data_df.columns = retrieve_column_name('stock_db', 'daily_price_tb')

data_df['MA_3'] = data_df.groupby('code')['CLOSE'].apply(lambda x: x.rolling(window=3).mean())
data_df['MA_5'] = data_df.groupby('code')['CLOSE'].apply(lambda x: x.rolling(window=5).mean())
data_df['MA_10'] = data_df.groupby('code')['CLOSE'].apply(lambda x: x.rolling(window=10).mean())
data_df['MA_20'] = data_df.groupby('code')['CLOSE'].apply(lambda x: x.rolling(window=20).mean())
data_df['MA_60'] = data_df.groupby('code')['CLOSE'].apply(lambda x: x.rolling(window=60).mean())
data_df['MA_3_5'] = data_df['MA_3'] - data_df["MA_5"]
data_df['MA_5_10'] = data_df['MA_5'] - data_df["MA_10"]
data_df['MA_10_20'] = data_df['MA_10'] - data_df["MA_20"]
data_df['MA_20_60'] = (data_df['MA_20'] - data_df["MA_60"]) 
data_df = data_df[data_df['time'] >= pre_3_date]
data_df = data_df[data_df['MA_3_5'] > 0]
data_df = data_df[data_df['MA_5_10'] > 0]
data_df = data_df[data_df['MA_10_20'] > 0]
data_df = data_df[data_df['MA_20_60'] > 0]

print data_df