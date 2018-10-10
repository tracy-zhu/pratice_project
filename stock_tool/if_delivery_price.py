# -*- coding: utf-8 -*-
"""

# 计算IF的到期之后的交割价格，是按照交割当天最后两个小时的算术平均价进行计算

Thu 2018/03/19

@author: Tracy Zhu
"""

# 导入系统库
import sys

# 导入用户库
sys.path.append("..")
from stock_tool.find_defensive_stock import *


def get_hs300_df(start_time, end_time):
    sql_sentence = "SELECT * FROM min_market_ths_db.000300_sh_min_tb where time > \"{start_time}\" and time <= \"{end_time}\""\
        .format(start_time=start_time, end_time=end_time)
    tp_table = fetchall_sql(sql_sentence)
    df_table = pd.DataFrame(list(tp_table), columns=['time', 'thscode', 'open', 'high', 'low', 'close', 'volume', 'amt', 'pct_chg',
                                                     'ex_chg', 'np', 'wp', 'buy_amt', 'sell_amt'])
    return df_table

if __name__ == '__main__':
    start_time = '2018-03-16 13:00:00'
    end_time = '2018-03-16 15:00:00'
    df_table = get_hs300_df(start_time, end_time)
    print "delivery price is " + str(df_table.close.mean())