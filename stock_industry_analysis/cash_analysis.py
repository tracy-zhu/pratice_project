# -*- coding: utf-8 -*-
"""

# 在存量博弈的市场环境下，找出成交金额占比比较高的股票，板块

# 和成交金额异动比较大的板块；

Fri 2018/06/15

@author: Tracy Zhu
"""

# 导入系统库
import sys

# 导入用户库
sys.path.append("..")
from stock_base.stock_industry_base import *
from datetime import date

out_file_folder = '..\\stock_industry_analysis\\result\\'

# trading_date = datetime.now()
# trading_day = trading_date.strftime('%Y-%m-%d')
trading_day = '2018-06-14'

all_stock_list = get_all_stock_code_list(trading_day)


def sort_stock_by_trade_amount(trading_day):
    """
    根据股票日线数据将当天所有的股票的成交金额进行排序
    :param stock_code:
    :param trading_day:
    :return:
    """
    out_file_folder = '..\\stock_industry_analysis\\result\\'
    sql = 'SELECT * FROM stock_db.daily_price_tb WHERE time  = \"{trading_day}\"'.format(trading_day=trading_day)
    tp_table = fetchall_sql(sql)
    df_table = pd.DataFrame(list(tp_table))
    df_table.columns = retrieve_column_name('stock_db', 'daily_price_tb')
    df_table = df_table[df_table.AMT > 0]
    sort_df = df_table.sort_values(by='AMT', axis=0, ascending=False)
    out_file_folder = out_file_folder + '\\' + trading_day + '\\'
    isExists = os.path.exists(out_file_folder)
    if not isExists:
        os.makedirs(out_file_folder)
    out_file_name = out_file_folder + 'trade_amount_sort.csv'
    f = open(out_file_name, 'wb')
    for index in sort_df.head(200).index:
        stock_code = sort_df.code[index]
        trade_amount = sort_df.AMT[index]
        chi_name = find_stock_chi_name(stock_code)
        print >>f, chi_name, ',', stock_code, ',', trade_amount
    f.close()
    return sort_df


def sort_stock_buy_amount_change(trading_day, ma_num):
    """
    筛选成交金额相对于过去变化比较大的股票
    :param trading_day:
    :param ma_num:和过去多少天的平均成交额做比较
    :return:
    """
    select_stock_list = []
    out_file_folder = '..\\stock_industry_analysis\\result\\'
    start_date = get_next_trading_day_stock(trading_day, -2 * ma_num)
    sql = 'SELECT * FROM stock_db.daily_price_tb WHERE time  >= \"{start_date}\" AND time ' \
          ' <=  \"{end_date}\"'.format(start_date=start_date, end_date=trading_day)
    tp_table = fetchall_sql(sql)
    data_df = pd.DataFrame(list(tp_table))
    data_df.columns = retrieve_column_name('stock_db', 'daily_price_tb')

    year = int(trading_day.split('-')[0])
    month = int(trading_day.split('-')[1])
    days = int(trading_day.split('-')[-1])
    now_date = date(year, month, days)

    data_df['rolling_amt'] = data_df.groupby('code')['AMT'].apply(lambda x: x.rolling(window=ma_num).mean())
    data_df['rolling_amt'] = data_df.groupby('code')['rolling_amt'].apply(lambda x: x.shift(1))
    data_df['amt_ratio'] = data_df['AMT'] / data_df['rolling_amt']
    data_df['price_change'] = data_df.groupby('code')['CLOSE'].apply(lambda x: (x - x.shift(3)) / x.shift(3))
    select_df = data_df[data_df.time == now_date]
    select_df = select_df[select_df.price_change > 0.01]
    sort_df = select_df.sort_values(by='amt_ratio', axis=0, ascending=False)
    out_file_folder = out_file_folder + '\\' + trading_day + '\\'
    isExists = os.path.exists(out_file_folder)
    if not isExists:
        os.makedirs(out_file_folder)
    out_file_name = out_file_folder + 'trade_amount_chg_sort.csv'
    bottom_stock_list = find_bottom_stock(trading_day)
    f = open(out_file_name, 'wb')
    for index in sort_df.head(200).index:
        stock_code = sort_df.code[index]
        if stock_code in bottom_stock_list:
            select_stock_list.append(stock_code)
            amt_ratio = sort_df.amt_ratio[index]
            chi_name = find_stock_chi_name(stock_code)
            print >>f, chi_name, ',', stock_code, ',', amt_ratio
    f.close()
    return select_stock_list


def find_stock_industry_sort(stock_list, trading_day, level_flag):
    """
    找出筛选的股票分别对应一级或者二级市场的代码列表，比较哪个行业在筛选的行业里出现的次数最多。
    :param sort_df:
    :param trading_day:
    :param level_flag:
    :return:
    """
    industry_dict = defaultdict(list)
    industry_df = get_industry_df(trading_day, level_flag)
    for stock_code in stock_list:
        block_code, block_name = find_stock_industry_name(stock_code, industry_df)
        industry_dict[block_code].append(stock_code)
    return industry_dict


def print_out_industry_proportion(industry_dict, industry_df):
    out_file_name = out_file_folder + 'industry_proportion.csv'
    f = open(out_file_name, 'wb')
    for industry_code, stock_code_list in industry_dict.items():
        all_stock_code_list = get_industry_stock_code(industry_df, industry_code)
        print >>f, industry_code, ",", len(stock_code_list), ',', len(all_stock_code_list)
    f.close()



if __name__ == '__main__':
    trading_day = '2018-07-18'
    ma_num = 10
    level_flag = 1
    sort_df_by_amount = sort_stock_by_trade_amount(trading_day)
    sort_df_by_amt_chg_stock_code = sort_stock_buy_amount_change(trading_day, ma_num)
    industry_dict = find_stock_industry_sort(sort_df_by_amt_chg_stock_code, trading_day, level_flag)
    industry_df = get_industry_df(trading_day, level_flag)
    print_out_industry_proportion(industry_dict, industry_df)
