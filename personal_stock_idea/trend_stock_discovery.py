# -*- coding: utf-8 -*-
"""

# 脚本在于发现类似与片仔癀这样的股票，首先根据以下的几种条件作为筛选；
# 1.回调的都很浅，不会大破均线
# 2. 筛选公司标的比较好的股票，市值上百亿，去除掉波动很大的风险， 市值不要超过千亿，避免中国平安这种涨不动的行情；
# 3.在过去的一段时间，涨幅为正的概率很高，并且并不是暴涨暴跌（去除掉妖股这些）；
# 4. 平均换手率很低（实际的流通股比较少，大部分被机构或者个人投资者持有）

Tue 2018/5/23

@author: Tracy Zhu
"""
# 导入系统库
import sys

# 导入用户库：
sys.path.append("..")
from stock_base.stock_volatility_generation import *

start_date = "2018-02-08"
end_date = "2018-05-25"
limit_positive_pct = 0.6


def calc_stock_performance(stock_code, start_date, end_date):
    """
    获取stock在指定期间平均的回撤大小，平均换手率等
    :param stock_code:
    :param start_date:
    :param end_date:
    :return:
    """
    stock_df = get_stock_df(stock_code, start_date, end_date)
    pct_series = stock_df['PCT_CHG']
    pct_series = pct_series[pct_series > -20]
    negative_pct_series = pct_series[pct_series < 0]
    negative_average = negative_pct_series.mean()
    free_turn_series = stock_df.FREE_TURN
    free_turn_series = free_turn_series[free_turn_series > 0]
    mean_free_turn = free_turn_series.mean()
    return negative_average, mean_free_turn


def stock_sort_by_drawback(stock_code_list, start_date, end_date):
    """
    将股票按照指定区间按照最大回撤的平均值进行排序
    :param stock_code:
    :param start_date:
    :param end_date:
    :return:
    """
    drawback_stock_dict = defaultdict()
    free_turn_dict = defaultdict()
    for stock_code in stock_code_list:
        negative_average, mean_free_turn = calc_stock_performance(stock_code, start_date, end_date)
        drawback_stock_dict[stock_code] = negative_average
        free_turn_dict[stock_code] = mean_free_turn
    sorted_drawback_stock = sorted(drawback_stock_dict.items(), key=lambda d: d[1])
    sorted_free_turn_stock = sorted(free_turn_dict.items(), key=lambda d: d[1])
    return sorted_drawback_stock, sorted_free_turn_stock


sql = 'SELECT * FROM stock_db.daily_price_tb WHERE time  >= \"{start_date}\" AND time ' \
      ' <=  \"{end_date}\"'.format(start_date=start_date, end_date=end_date)
tp_table = fetchall_sql(sql)
data_df = pd.DataFrame(list(tp_table))
data_df.columns = retrieve_column_name('stock_db', 'daily_price_tb')

data_df['pct_chg_flag'] = data_df['PCT_CHG'] > 0
positive_pct_above = data_df.groupby('code')['pct_chg_flag'].apply(lambda x: float(x.sum()) / float(len(x)))
positive_pct_above = positive_pct_above[positive_pct_above >= limit_positive_pct]

raw_stock_list = positive_pct_above.index
select_stock_list = delete_new_stock(raw_stock_list, 100, end_date)
select_series = positive_pct_above[select_stock_list]
# volatility_sort_stock = volatility_sort(select_stock_list, end_date, period=60, flag=2)
sorted_drawback_stock, sorted_free_turn_stock = stock_sort_by_drawback(select_stock_list, start_date, end_date)

for value in sorted_drawback_stock:
    if value[0] == '600436.SH':
        print value