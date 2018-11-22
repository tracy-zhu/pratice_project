# -*- coding: utf-8 -*-
"""

# 考虑到布伦特原油对大盘择时的影响

Mon 2018/11/05

@author: Tracy Zhu
"""

import sys

# 导入用户库
sys.path.append("..")
from stock_base.stock_option_base import *
from python_base.plot_method import *

data_file_name = '.\\fundamental_research\\data\\SPGSBRTR_all_a_index.csv'

oil_df = pd.read_csv(data_file_name, index_col='DateTime')
oil_df = oil_df.dropna(how='any')
oil_df['SPG_shift'] = oil_df['SPGSBRTR.SPI'].shift(5)
oil_df['SPG_pct_chg'] = (oil_df['SPGSBRTR.SPI'] - oil_df['SPGSBRTR.SPI'].shift(1)) /  oil_df['SPGSBRTR.SPI'].shift(1)
oil_df['pct_chg'] = (oil_df['881001.WI'] - oil_df['881001.WI'].shift(1)) / oil_df['881001.WI'].shift(1)
oil_df['SPG_pct_chg_shift'] = oil_df['SPG_pct_chg'].shift(5)


fig, ax = plt.subplots()
ax.plot(oil_df['881001.WI'], color='r', label="wind all a index")
ax1 = ax.twinx()
# ax1.plot(oil_df['SPG_shift'], color="b", label="SPG shift")
ax1.plot(oil_df['SPGSBRTR.SPI'], color="b", label="SPG index")
ax.legend(loc="upper left")
ax1.legend(loc="upper right")
title = "wind all a index and SPG index"
plt.title(title)
fig.set_size_inches(23.2, 14.0)


def back_test_for_oil(oil_df):
    """
    通过原油的5期前的收益率做择时，当前5期的收益率为正，
    则当月做空该指数，否则当月做多该指数；
    :param oil_df:
    :return:
    """
    oil_df['direction'] = 0
    oil_df.loc[oil_df['SPG_pct_chg_shift'] < 0, 'direction'] = 1
    oil_df['strategy_pct_chg'] = oil_df['pct_chg'] * oil_df['direction']
    oil_df = oil_df.dropna(how='any')
    index_cumprod = (oil_df['pct_chg'] + 1).cumprod()
    strategy_cumprod =(oil_df['strategy_pct_chg'] + 1).cumprod()
    index_cumprod.plot()
    strategy_cumprod.plot()
