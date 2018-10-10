# -*- coding: utf-8 -*-
"""

# 筛选股票相对于之前，连续三天放大的股票；

# 由此找出市场突然关注的股票

Tue 2018/4/11

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

start_date = "2018-06-01"
end_date = "2018-07-18"
pre_3_date_str = get_next_trading_day_stock(end_date, -2)
pre_3_date = change_trading_day_date_stock(pre_3_date_str)

sql = 'SELECT * FROM stock_db.daily_price_tb WHERE time  >= \"{start_date}\" AND time ' \
      ' <=  \"{end_date}\"'.format(start_date=start_date, end_date=end_date)
tp_table = fetchall_sql(sql)
data_df = pd.DataFrame(list(tp_table))
data_df.columns = retrieve_column_name('stock_db', 'daily_price_tb')

data_df['rolling_amt'] = data_df.groupby('code')['AMT'].apply(lambda x: x.rolling(window=10).mean())
data_df['rolling_amt'] = data_df.groupby('code')['rolling_amt'].apply(lambda x: x.shift(1))
data_df['amt_ratio'] = data_df['AMT'] / data_df['rolling_amt']
data_df['amt_ratio_flag'] = data_df['amt_ratio'] > 2
select_data_df = data_df[data_df['time'] == pre_3_date]
grouped = select_data_df.groupby('code')['amt_ratio_flag'].sum()
selected_grouped = grouped[grouped.values > 2]
print selected_grouped


def plot_free_turn(stock_code, start_date, end_date):
    """
    画出某只股票的，过去一段时间换手率的曲线
    :param stock_code:
    :param start_date:
    :param end_date:
    :return:
    """
    stock_df = get_stock_df(stock_code, start_date, end_date)
    stock_df.FREE_TURN.plot()

if __name__ == '__main__':
    stock_code = '002787.SZ'
    start_date = '2018-04-26'
    end_date = '2018-06-07'
