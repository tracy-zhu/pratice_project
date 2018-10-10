# -*- coding: utf-8 -*-
"""

# 找出当前交易日成交量放大排名前50的股票；

# 分析这个股票分别都属于哪些板块，找出占比比较多的板块

Fri 2018/07/31

@author: Tracy Zhu
"""

# 导入系统库
import sys

# 导入用户库
sys.path.append("..")
from stock_base.stock_industry_base import *

out_file_folder = '..\\stock_industry_analysis\\result\\'
stock_file_folder = "V:\\"

limit_pre_pct = 20
limit_bit_pin_ratio = 0.5
limit_turnover_rate = 1.5


def sort_stock_by_volume_ratio(trading_day, ma_num):
    """
    筛选成交金额相对于过去变化比较大的股票
    :param trading_day:
    :param ma_num:和过去多少天的平均成交额做比较
    :return:
    """
    start_date = get_next_trading_day_stock(trading_day, -2 * ma_num)
    sql = 'SELECT * FROM stock_db.daily_price_tb WHERE time  >= \"{start_date}\" AND time ' \
          ' <=  \"{end_date}\"'.format(start_date=start_date, end_date=trading_day)
    tp_table = fetchall_sql(sql)
    data_df = pd.DataFrame(list(tp_table))
    data_df.columns = retrieve_column_name('stock_db', 'daily_price_tb')
    data_df.VOLUME = data_df.VOLUME.replace(0, np.nan)

    now_date = change_trading_day_date_stock(trading_day)

    data_df['rolling_vol'] = data_df.groupby('code')['VOLUME'].apply(lambda x: x.rolling(window=ma_num).mean())
    data_df['rolling_vol'] = data_df.groupby('code')['rolling_vol'].apply(lambda x: x.shift(1))
    data_df['rolling_turnover_rate'] = data_df.groupby('code')['FREE_TURN'].apply(lambda x: x.rolling(window=ma_num).mean())
    data_df['rolling_turnover_rate'] = data_df.groupby('code')['rolling_turnover_rate'].apply(lambda x: x.shift(1))
    data_df['vol_ratio'] = data_df['VOLUME'] / data_df['rolling_vol']
    data_df['pre_price_change'] = data_df.groupby('code')['CLOSE'].apply(lambda x: (x - x.shift(3)) / x.shift(3))
    data_df['is_exists'] = (data_df["HIGH"] - data_df["LOW"])
    data_df = data_df[data_df['is_exists'] != 0]
    data_df['day_pct'] =  data_df.CLOSE - data_df.OPEN
    data_df = data_df[data_df['day_pct'] > 0]
    data_df['bit_pin_ratio'] = (data_df["HIGH"] - data_df["CLOSE"]) / (data_df["HIGH"] - data_df["LOW"])
    data_df = data_df[data_df['bit_pin_ratio'] < 0.5]
    select_df = data_df[data_df.time == now_date]
    select_df = select_df[select_df.pre_price_change < 0.2]
    select_df = select_df[select_df.FREE_TURN <= limit_turnover_rate]
    sort_df = select_df.sort_values(by='vol_ratio', axis=0, ascending=False)
    sort_df = sort_df.head(50)
    return sort_df


def sort_stock_by_volume_ratio_real_time(trading_day, ma_num):
    """
    筛选成交金额相对于过去变化比较大的股票
    跟上面的函数不同的是，在收盘的时候直接下载，而不是通过数据库下载；
    :param trading_day: '2018-06-15'
    :param ma_num:和过去多少天的平均成交额做比较
    :return:
    """
    pre_trading_day = get_pre_trading_day_stock(trading_day)
    start_date = get_next_trading_day_stock(trading_day, -2 * ma_num)
    sql = 'SELECT * FROM stock_db.daily_price_tb WHERE time  >= \"{start_date}\" AND time ' \
          ' <=  \"{end_date}\"'.format(start_date=start_date, end_date=pre_trading_day)
    tp_table = fetchall_sql(sql)
    data_df = pd.DataFrame(list(tp_table))
    data_df.columns = retrieve_column_name('stock_db', 'daily_price_tb')
    data_df.VOLUME = data_df.VOLUME.replace(0, np.nan)
    real_time_df = get_today_data_df(trading_day)
    new_index = real_time_df.index + len(data_df)
    columns_names = ["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME", "AMT", "FREE_TURN", "code", "time"]
    real_time_df = DataFrame(real_time_df.values, index=new_index, columns=columns_names)
    data_df = pd.concat([data_df, real_time_df], axis=0)

    now_date = change_trading_day_date_stock(trading_day)

    data_df['rolling_vol'] = data_df.groupby('code')['VOLUME'].apply(lambda x: x.rolling(window=ma_num).mean())
    data_df['rolling_vol'] = data_df.groupby('code')['rolling_vol'].apply(lambda x: x.shift(1))
    data_df['rolling_turnover_rate'] = data_df.groupby('code')['FREE_TURN'].apply(lambda x: x.rolling(window=ma_num).mean())
    data_df['rolling_turnover_rate'] = data_df.groupby('code')['rolling_turnover_rate'].apply(lambda x: x.shift(1))
    data_df['vol_ratio'] = data_df['VOLUME'] / data_df['rolling_vol']
    data_df['pre_price_change'] = data_df.groupby('code')['CLOSE'].apply(lambda x: (x - x.shift(3)) / x.shift(3))
    data_df['is_exists'] = (data_df["HIGH"] - data_df["LOW"])
    data_df = data_df[data_df['is_exists'] != 0]
    data_df['day_pct'] =  data_df.CLOSE - data_df.OPEN
    data_df = data_df[data_df['day_pct'] > 0]
    data_df['bit_pin_ratio'] = (data_df["HIGH"] - data_df["CLOSE"]) / (data_df["HIGH"] - data_df["LOW"])
    data_df = data_df[data_df['bit_pin_ratio'] < 0.5]
    select_df = data_df[data_df.time == trading_day]
    select_df = select_df[select_df.pre_price_change < 0.2]
    select_df = select_df[select_df.FREE_TURN <= limit_turnover_rate]
    sort_df = select_df.sort_values(by='vol_ratio', axis=0, ascending=False)
    sort_df = sort_df.head(50)
    return sort_df


def get_today_data_df(trading_day):
    """
    从wind上下载当天的data_df,然后和数据库下载的data_df合并
    :param trading_day:
    :return:
    """
    file_name = stock_file_folder + "\\temp\\haoran_close_data\\" + trading_day + '.csv'
    real_time_df = pd.read_csv(file_name)
    real_time_df = real_time_df.drop(["Unnamed: 0", "RT_DATE"], axis=1)
    columns_names = ["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME", "AMT", "FREE_TURN", "code", "time"]
    real_time_df = DataFrame(real_time_df.values, columns=columns_names)
    return real_time_df


def select_df_out(select_df, trading_day):
    global out_file_folder
    out_file_folder = out_file_folder + '\\' + trading_day + '\\'
    isExists = os.path.exists(out_file_folder)
    if not isExists:
        os.makedirs(out_file_folder)
    out_file_name = out_file_folder + 'trade_volume_chg_sort.xlsx'
    select_df.to_excel(out_file_name)


def find_stock_industry_sort(select_df, industry_df):
    """
    找出筛选的股票分别对应一级或者二级市场的代码列表，比较哪个行业在筛选的行业里出现的次数最多。
    :param sort_df:
    :param trading_day:
    :param level_flag:
    :return:
    """
    industry_dict = defaultdict(list)
    stock_list = select_df.code
    for stock_code in stock_list:
        print stock_code
        block_code, block_name = find_stock_industry_name(stock_code, industry_df)
        if block_code != None:
            industry_dict[block_code].append(stock_code)
    return industry_dict


def print_out_industry_proportion(industry_dict, industry_df):
    out_file_name = out_file_folder + 'industry_volume_proportion.csv'
    f = open(out_file_name, 'wb')
    for industry_code, stock_code_list in industry_dict.items():
        all_stock_code_list = get_industry_stock_code(industry_df, industry_code)
        print >>f, industry_code, ",", len(stock_code_list), ',', len(all_stock_code_list)
    f.close()


def print_out_most_industry_dict(industry_dict):
    """
    将筛选股票最多的板块的几只股票打印出来；
    :param industry_dict:
    :return:
    """
    out_file_name = out_file_folder + 'most_stock_industry.csv'
    f = open(out_file_name, 'wb')
    industry_count_dict = defaultdict()
    for industry_code, stock_code_list in industry_dict.items():
        count_num = len(stock_code_list)
        industry_count_dict[industry_code] = count_num
    sort_industry_list = sorted(industry_count_dict.items(), key=lambda d:d[1], reverse=True)
    # industry_code = sort_industry_list[0][0]
    for industry_code_item in sort_industry_list[:3]:
        industry_code = industry_code_item[0]
        str_line = industry_code + '\n'
        f.write(str_line)
        stock_code_list = industry_dict[industry_code]
        for stock_code in stock_code_list:
            stock_chi_name = find_stock_chi_name(stock_code)
            str_line = stock_code + ',' + stock_chi_name + '\n'
            f.write(str_line)
    f.close()


def find_concept_num(select_code_list, trading_day):
    """
    找出每个股票对应的板块，并找出出现最多的板块
    :param select_code_list:
    :return:
    """
    concept_list = []
    pre_trading_day = get_pre_trading_day_stock(trading_day)
    for select_code in select_code_list:
        concept_stock_list = find_stock_concept(select_code, pre_trading_day)
        concept_list = concept_list + concept_stock_list
    counts = dict()
    for concept_name in concept_list:
        if concept_name in counts:
            counts[concept_name] += 1
        else:
            counts[concept_name] = 1
    sort_counts = sorted(counts.items(), key=lambda  d:d[1], reverse=True)

    concept_out_file_name = out_file_folder + "\\concept_value_counts.txt"
    f2 = open(concept_out_file_name, 'wb')
    for concept_name, num in sort_counts:
        concept_str = concept_name.split(',')[1]
        print>>f2, concept_str, ',', num
    f2.close()
    return sort_counts


if __name__ == '__main__':
    # trading_date = datetime.now()
    # trading_day = trading_date.strftime('%Y-%m-%d')
    trading_day = '2018-09-05'
    ma_num = 5
    level_flag = 2
    # select_df = sort_stock_by_volume_ratio(trading_day, ma_num)
    select_df = sort_stock_by_volume_ratio_real_time(trading_day, ma_num)
    select_df_out(select_df, trading_day)
    industry_df = get_industry_df(trading_day, level_flag)
    # industry_df = get_industry_df_test()
    industry_dict = find_stock_industry_sort(select_df, industry_df)
    print_out_industry_proportion(industry_dict, industry_df)
    print_out_most_industry_dict(industry_dict)
    stock_code_list = list(select_df.code)
    sort_concept_counts = find_concept_num(stock_code_list, trading_day)
