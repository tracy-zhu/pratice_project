# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 08:50:21 2018

@author: hp
"""


import sys
import pymysql

# 导入用户库
sys.path.append("..")
from datetime import date
from python_base.common_method import *
from stock_base.stock_constant import *


def connect_mysql():
    conn = pymysql.connect(host = "192.168.1.205",
                         user = "stock",
                         passwd = "112233",
                         port = 3308,
#                         db = "factor_db", \
                         local_infile=1)
    conn.set_charset('utf8')  
    cursor = conn.cursor()
    cursor.execute('SET NAMES utf8;')  
    cursor.execute('SET character_set_connection=utf8;')  
    return (cursor,conn)


def execute_sql(sql):
    (cursor,conn) = connect_mysql()
    try:
        print(sql)
        cursor.execute(sql)
        conn.commit()
        print('...execute successfull!')
    except Exception as e:
        conn.rollback()
        print('...have problem, already rollback!')
        print(e)
    conn.close()


def fetchall_sql(sql):
    (cursor, conn) = connect_mysql()
    try:
        print(sql)
        cursor.execute(sql)
        res = cursor.fetchall()
        print('...execute successfull!')
    except Exception as e:
        conn.rollback()
        print('...have problem, already rollback!')
        print(e)
    conn.close()
    return res

        
def retrieve_table(db_name, table_name, time_name, start_date, end_date):
    sql = 'SELECT * FROM ' + db_name + '.' + table_name + ' WHERE ' + time_name + " >='" + \
    start_date + "' AND " + time_name + " <='" + end_date + "'"
    
    tp_table = fetchall_sql(sql)
    df_table = pd.DataFrame(list(tp_table))
    df_table.columns = retrieve_column_name('stock_db', 'daily_price_tb')
    
    return df_table


def get_stock_df(stock_code, start_date, end_date):
    """
    将股票start_date, end_date的日期的df选出来
    :param stock_code:
    :param start_date:
    :param end_date:
    :return:
    """
    sql = 'SELECT * FROM stock_db.daily_price_tb WHERE time  >= \"{start_date}\" AND time ' \
          ' <=  \"{end_date}\" and code = \"{stock_code}\"'.format(start_date=start_date, end_date=end_date, stock_code=stock_code)
    tp_table = fetchall_sql(sql)
    df_table = pd.DataFrame(list(tp_table))
    if len(df_table) > 0:
        df_table.columns = retrieve_column_name('stock_db', 'daily_price_tb')
    return df_table


def get_stock_df_qfq(stock_code, start_date, end_date):
    """
    这个股票筛选的是前复权数据
    将股票start_date, end_date的日期的df选出来
    :param stock_code:
    :param start_date:
    :param end_date:
    :return:
    """
    sql = 'SELECT * FROM stock_db.daily_price_qfq_tb WHERE time  >= \"{start_date}\" AND time ' \
          ' <=  \"{end_date}\" and code = \"{stock_code}\"'.format(start_date=start_date, end_date=end_date, stock_code=stock_code)
    tp_table = fetchall_sql(sql)
    df_table = pd.DataFrame(list(tp_table))
    if len(df_table) > 0:
        df_table.columns = retrieve_column_name('stock_db', 'daily_price_tb')
    return df_table


def get_stock_list_description(stock_code_list, trading_day, back_period):
    """
    计算股票列表，在指定区间的一些数据特征，现在主要是区间涨跌幅这个特征；
    返回一个series，index是每个stock_code, 后面的是区间涨幅；
    :param stock_code_list : list
    :param trading_day: '2018-06-15'
    """
    pct_chg_dict = defaultdict()
    start_date = get_next_trading_day_stock(trading_day, -1 * back_period)
    for stock_code in stock_code_list:
        print(stock_code, start_date, trading_day)
        stock_df = get_stock_df(stock_code, start_date, trading_day)
        if len(stock_df) > 0:
            stock_df = stock_df[stock_df.PCT_CHG > -100]
            if len(stock_df) > 0:
                sum_pct_chg = (stock_df.PCT_CHG / 100 + 1).cumprod().values[-1]
                pct_chg_dict[stock_code] = sum_pct_chg
    pct_chg_series = Series(pct_chg_dict)
    return pct_chg_series


def retrieve_column_name(db_name, table_name):
    sql = "SELECT `COLUMN_NAME` FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='" + db_name + "' AND `TABLE_NAME`='" + table_name + "';"        
    res = fetchall_sql(sql)
    return [res[i][0] for i in np.arange(len(res))]


def get_ipo_date_df():
    sql =  'SELECT * FROM stock_db.ipo_delist_date'
    tp_table = fetchall_sql(sql)
    df_table = pd.DataFrame(list(tp_table), columns=['code', 'name', 'list_date', 'delist_date'])
    return df_table


def delete_new_stock(stock_code_list, limit_days, reference_day):
    """
    根据参考天数往前推limit_days的日期，晚于那个日期上市的股票都当做新股删除掉;
    :param stock_code_list:
    :param limit_days:
    :param reference_day:"2018-01-31"
    :return:
    """
    delete_stock_list = []
    ipo_date_df = get_ipo_date_df()
    reference_datetime = datetime.strptime(reference_day, "%Y-%m-%d")
    limit_date = reference_datetime - timedelta(days=limit_days)
    for stock_code in stock_code_list:
        select_df = ipo_date_df[ipo_date_df['code'] == stock_code]
        if len(select_df) > 0:
            list_date = select_df['list_date'].values[0]
            list_date_time = datetime.strptime(str(list_date), '%Y-%m-%d')
            if list_date_time < limit_date:
                delete_stock_list.append(stock_code)
    return delete_stock_list


def get_index_data(index_code, start_date, end_date):
    """
    获取指数的数据，转化为df
    :param index_code: 指数代码 000300.SH
    :param start_date:
    :param end_date:
    :return:
    """
    sql =  'SELECT * FROM daily_market_ths_db.' + index_code[:-3] + "_" + index_code[-2:].lower() + "_tb" +\
           " where time >= \"{start_date}\" and time <= \"{end_date}\"".format(start_date=start_date, end_date=end_date)
    tp_table = fetchall_sql(sql)
    df_table = pd.DataFrame(list(tp_table), columns=['time', 'code', 'open', 'high', 'low', 'close', 'pct_chg',
                                                     'volume', 'amt', 'free_turn'])
    return df_table


def get_index_minute_data(index_code, start_date, end_date):
    """
    获取指数的分钟数据
    :param index_code: 000300.SH
    :param trading_day:
    :return:
    """
    begin_time = start_date + " 09:30:00"
    end_time = end_date + ' 15:00:00'
    sql =  'SELECT * FROM min_market_ths_db.' + index_code[:-3] + "_" + index_code[-2:].lower() + "_min_tb" +\
           " where time >= \"{begin_time}\" and time <= \"{end_time}\"".format(begin_time=begin_time, end_time=end_time)
    tp_table = fetchall_sql(sql)
    df_table = pd.DataFrame(list(tp_table), columns=['time', 'thscode', 'open', 'high', 'low', 'close', 'volume','amt', 'pct_chg',
                                                     'ex_chg', 'np', 'wp', 'buy_amt', 'sell_amt'])
    return df_table


def transfer_index_minute_data_period(index_df, period):
    """
    将1分钟的分钟数据转换成5分钟，15分钟或者其他的数据，采取的是close的resample方法，所以只对价格数据有效
    :param index_df:
    :param period:
    :return:
    """
    index_df.index = index_df.time
    resample_df = index_df.resample(period).first()
    return resample_df


def get_index_period_yield(index_code, trading_day, begin_time, end_time):
    """
    获取指数某一段的收益
    :param index_code: 000300.SH str
    :param trading_day: '2018-03-26'
    :param begin_time: '09:30'
    :param end_time: '15:00'
    :return:
    """
    df_table = get_index_minute_data(index_code, trading_day)
    begin_period = trading_day + " " + begin_time + ":00"
    end_period = trading_day + ' ' + end_time + ":00"
    select_df = df_table[df_table.time >= begin_period]
    select_df = select_df[select_df.time <= end_period]
    begin_price = select_df.close.values[0]
    end_price = select_df.close.values[-1]
    period_yield = float(end_price) / float(begin_price) - 1
    return period_yield


def find_stock_up_limit(trading_day, direction):
    """
    找出当个交易日涨停板的股票
    :param trading_day:
    :direction: 1 : up_limit; -1, down_limit
    :return:
    """
    select_df = None
    sql_sentence = 'SELECT * FROM stock_db.stock_trade_status_tb where time = \"{trading_day}\"'.format(trading_day=trading_day)
    tp_table = fetchall_sql(sql_sentence)
    df_table = pd.DataFrame(list(tp_table), columns=['time', 'code', 'maxupordown', 'trade_status', 'susp_days', 'susp_reason'])
    if direction == 1:
        select_df = df_table[df_table['maxupordown'] == 1]
    elif direction == -1:
        select_df = df_table[df_table['maxupordown'] == -1]
    limit_stock_list = select_df.code
    delete_stock_list = delete_new_stock(limit_stock_list, 60, trading_day)
    return delete_stock_list


def stock_up_limit_days(stock_code):
    """
    找出一只股票在数据库中涨停的交易日日期
    :param stock_code:
    :return: list date格式的日期
    """
    up_limit_days = []
    sql_sentence = 'SELECT * FROM stock_db.stock_trade_status_tb where MAXUPORDOWN = 1 and code = \"{stock_code}\"'.format(stock_code=stock_code)
    tp_table = fetchall_sql(sql_sentence)
    select_df = pd.DataFrame(list(tp_table), columns=['time', 'code', 'maxupordown', 'trade_status', 'susp_days', 'susp_reason'])
    if len(select_df) > 0:
        up_limit_days = select_df.time
    return up_limit_days


def stock_is_up_limit_back_period(stock_code, trading_day, back_period):
    """
    找出当前交易日往前回看一段时间之后，有没有出现过涨停；
    ：param stock_code:
    : param trading_day:当个交易日：
    ：param back_period: 回看的日期；
    """
    flag = False
    start_date = get_next_trading_day_stock(trading_day,  -1 * back_period)
    end_date = get_next_trading_day_stock(trading_day, -1)
    sql_sentence = 'SELECT * FROM stock_db.stock_trade_status_tb where code = \"{stock_code}\" and' \
                   ' time >= \"{start_date}\" and time <= \"{end_date}\"'.format(stock_code=stock_code, start_date=start_date, end_date=end_date)
    tp_table = fetchall_sql(sql_sentence)
    up_date = None
    select_df = pd.DataFrame(list(tp_table), columns=['time', 'code', 'maxupordown', 'trade_status', 'susp_days', 'susp_reason'])
    select_df = select_df[select_df['maxupordown'] == 1]
    if len(select_df) > 0:
        up_date = str(select_df.time.values[-1])
        flag = True
    return flag, up_date


def stock_is_up_limit(stock_code, trading_day):
    """
    判断该股票是否涨停,在那个交易日是否涨停
    :param stock_code:
    :param trading_day:
    :return:
    """
    up_stock_list = find_stock_up_limit(trading_day, 1)
    if stock_code in up_stock_list:
        return True
    else:
        return False


def find_stock_concept(stock_code, trading_day):
    """
    找出股票在固定交易日对应的概念
    """
    sql_sentence = 'SELECT * FROM stock_db.concept_block_tb where date = \"{trading_day}\" and wind_code = \"{stock_code}\"'\
                    .format(trading_day=trading_day, stock_code=stock_code)
    tp_table = fetchall_sql(sql_sentence)
    df_table = pd.DataFrame(list(tp_table), columns=['date', 'wind_code', 'sec_name', 'block_code', 'block_name'])
    concat_name = df_table.block_code + "," + df_table.block_name
    concept_list = list(concat_name.values)
    return concept_list


def find_all_stock_concept_list(trading_day):
    """
    找出当个交易日，wind上所有的概念及其代码
    :param trading_day:
    :return:
    """
    sql_sentence = 'SELECT * FROM stock_db.concept_block_tb where date = \"{trading_day}\"'\
        .format(trading_day=trading_day)
    tp_table = fetchall_sql(sql_sentence)
    df_table = pd.DataFrame(list(tp_table), columns=['date', 'wind_code', 'sec_name', 'block_code', 'block_name'])
    concat_name = df_table.block_code + "," + df_table.block_name
    concept_all_list = concat_name.unique()
    out_file_name = "..\\stock_base\\result\\all_concept_list.txt"
    f = open(out_file_name, 'wb')
    for concept_name in concept_all_list:
        f.write(concat_name+'\n')
    f.close()
    return concept_all_list


def find_all_stock_concept_list_ifind(trading_day):
    """
    找出当个交易日，同花顺对应的所有概念代码
    :param trading_day:
    :return: "block_code, block_name"
    """
    sql_sentence = 'SELECT * FROM stock_db.concept_block_ths_tb where date = \"{trading_day}\"' \
        .format(trading_day=trading_day)
    tp_table = fetchall_sql(sql_sentence)
    df_table = pd.DataFrame(list(tp_table), columns=['date', 'wind_code', 'sec_name', 'block_code', 'block_name'])
    concat_name = df_table.block_code + "," + df_table.block_name
    concept_all_list = concat_name.unique()
    return concept_all_list


def find_stock_concept_ifind(stock_code, trading_day):
    """
    找出同花顺对应的股票对应的概念
    :param stock_code:
    :param trading_day:
    :return:
    """
    # stock_code = '603999.SH'
    # trading_day = '2018-03-16'
    sql_sentence = 'SELECT * FROM stock_db.concept_block_ths_tb where date = \"{trading_day}\" and the_code = \"{stock_code}\"' \
        .format(trading_day=trading_day, stock_code=stock_code)
    tp_table = fetchall_sql(sql_sentence)
    df_table = pd.DataFrame(list(tp_table), columns=['date', 'ths_code', 'sec_name', 'block_code', 'block_name'])
    concat_name = df_table.block_code + "," + df_table.block_name
    concept_list = list(concat_name.values)
    return concept_list


def find_concept_stock(concept_code, trading_day):
    """
    找出当个交易日的板块对应的股票代码
    :param concept_code:
    :param trading_day:
    :return:
    """
    sql_sentence = 'SELECT * FROM stock_db.concept_block_tb where date = \"{trading_day}\" and block_code = \"{concept_code}\"' \
        .format(trading_day=trading_day, concept_code=concept_code)
    tp_table = fetchall_sql(sql_sentence)
    df_table = pd.DataFrame(list(tp_table), columns=['date', 'wind_code', 'sec_name', 'block_code', 'block_name'])
    stock_code_list = list(df_table.wind_code)
    return stock_code_list


def find_concept_stock_ifind(concept_code, trading_day):
    """
    找出每个交易日板块对应的股票代码，同花顺式分的板块
    :param concept_code:
    :param trading_day:
    :return:
    """
    sql_sentence = 'SELECT * FROM stock_db.concept_block_ths_tb where date = \"{trading_day}\" and block_code = \"{concept_code}\"' \
        .format(trading_day=trading_day, concept_code=concept_code)
    tp_table = fetchall_sql(sql_sentence)
    df_table = pd.DataFrame(list(tp_table), columns=['date', 'the_code', 'sec_name', 'block_code', 'block_name'])
    stock_code_list = list(df_table.the_code)
    return stock_code_list


def find_stock_up_limit_time(stock_code, trading_day):
    """
    根据分钟数据找出股票涨停的时间
    :param stock_code:
    :param trading_day:
    :return:
    """
    is_always_up_limit = None
    start_time = trading_day + ' 09:30:00'
    end_time = trading_day + ' 15:00:00'
    sql_sentence = 'SELECT * FROM stock_db.minute_infor_tb where time >= \"{start_time}\" and time <= \"{end_time}\" and thscode = \"{stock_code}\"' \
        .format(start_time=start_time, end_time=end_time, stock_code=stock_code)
    tp_table = fetchall_sql(sql_sentence)
    df_table = pd.DataFrame(list(tp_table), columns=['time', 'thscode', 'open', 'high', 'low','close', 'volume', 'amt',
                                                     'pct_chg', 'ex_chg', 'np', 'wp', 'buy_amt', 'sell_amt'])
    df_table.index = df_table.time
    np_series = df_table.np
    np_series = np_series.replace(-999,0)
    np_zeros_series = np_series[np_series == 0]
    first_up_limit_time = np_zeros_series.index[0]
    np_series_after_first_limit = np_series[np_series.index > first_up_limit_time]
    np_unzero_series = np_series_after_first_limit[np_series_after_first_limit != 0]
    if len(np_unzero_series) == 0:
        "代表一直涨停"
        is_always_up_limit = 1
    else:
        "代表后面有打开"
        is_always_up_limit = 0
    return first_up_limit_time, is_always_up_limit


def find_stock_up_limit_time_from_raw_data(stock_code, trading_day):
    """
    根据分钟数据找出股票涨停的时间
    :param stock_code:
    :param trading_day:
    :return:
    """
    is_always_up_limit = None
    first_up_limit_time = None
    file_name = stock_code.split('.')[0] + "_" + stock_code.split('.')[1] + '_' + trading_day + '.csv'
    data_file_name = stock_minute_file_path + file_name
    try:
        df_table = pd.read_csv(data_file_name)
    except:
        print("there is no file name " + file_name)
    else:
        start_time = trading_day + ' 09:30'
        df_table.index = df_table.time
        high_price_series = df_table.high
        high_price_series = high_price_series.dropna()
        high_price_series = high_price_series[high_price_series.index > start_time]
        up_limit_price = high_price_series.max()
        up_limit_series = high_price_series[high_price_series >= up_limit_price]
        first_up_limit_time = up_limit_series.index[0]
        high_series_after_first_limit = high_price_series[high_price_series.index >= first_up_limit_time]
        if len(high_series_after_first_limit) > len(up_limit_series):
            "代表一直涨停"
            is_always_up_limit = 0
        else:
            "代表后面有打开"
            is_always_up_limit = 1
    return first_up_limit_time, is_always_up_limit


# ----------------------------------------------------------------------
# 根据当个交易日股票后n个交易日的交易日期
def get_next_trading_day_stock(trading_day, holding_days):
    "股票日期格式为2018-03-05"
    end_date = None
    trading_day_list = get_trading_day_list()
    trading_day = ''.join(trading_day.split("-"))
    trading_day_index = trading_day_list.index(trading_day+'\n')
    if (trading_day_index + holding_days) < len(trading_day_list):
        end_date = trading_day_list[trading_day_index + holding_days][:-1]
        end_date = end_date[:4] + '-' + end_date[4:6] + '-' + end_date[6:8]
    else:
        end_date = trading_day_list[-1]
        end_date = end_date[:4] + '-' + end_date[4:6] + '-' + end_date[6:8]
    return end_date


def find_stock_chi_name(stock_code):
    """
    根据股票代码将股票的中文名字输出
    :param stock_code:
    :return:
    """
    sql =  'SELECT * FROM stock_db.ipo_delist_date where code = \"{stock_code}\"'.format(stock_code=stock_code)
    tp_table = fetchall_sql(sql)
    chi_name = tp_table[0][1]
    return chi_name


def find_industry_chi_name(industry_code, level_flag):
    """
    根据行业代码将股票的中文名字输出
    :param stock_code:
    :return:
    """
    sql = ''
    trading_day = '2018-07-10'
    if level_flag == 1:
        sql =  'SELECT * FROM stock_db.sw_ind1_tb where block_code = \"{stock_code}\" and date = \"{trading_day}\"'.format(stock_code=industry_code, trading_day=trading_day)
    elif level_flag == 2:
        sql =  'SELECT * FROM stock_db.sw_ind2_tb where block_code = \"{stock_code}\" and date = \"{trading_day}\"'.format(stock_code=industry_code, trading_day=trading_day)
    tp_table = fetchall_sql(sql)
    chi_name = tp_table[0][-1]
    return chi_name


def read_stock_minute_data(stock_code, trading_day):
    """
    根据股票代码读取当天的分钟数据
    :param stock_code:
    :param trading_day:
    :return:
    """
    df_table = DataFrame()
    file_name = stock_code.split('.')[0] + "_" + stock_code.split('.')[1] + '_' + trading_day + '.csv'
    data_file_name = stock_minute_file_path + file_name
    try:
        df_table = pd.read_csv(data_file_name)
    except:
        print("there is no file name " + file_name)
    else:
        df_table.index = df_table.time
    return df_table


def read_stock_tick_data(stock_code, trading_day):
    """
    读取股票tick数据
    :param stock_code: 600300.SZ
    :param trading_day: '20180320'
    :return:
    """
    stock_df = DataFrame()
    stock_num = stock_code.split('.')[0]
    file_name = stock_tick_file_path + trading_day + '\\' + stock_num + '.csv'
    try:
        stock_df = pd.read_csv(file_name)
    except:
        print("there is no file for " + stock_code + " in " + trading_day)
    else:
        stock_df.index = stock_df.time
        stock_df = stock_df[stock_df.index >= 93000]
    return stock_df


def read_stock_tick_data_qian(stock_code, trading_day):
    """
    读取股票tick数据,和上面的函数不同的是读取的是钱哥的tick数据，比较稳定
    :param stock_code: 600300.SZ
    :param trading_day: '20180320'
    :return:
    """
    stock_df = DataFrame()
    stock_name = ('_').join(stock_code.split('.'))
    file_name = stock_tick_file_path_qian + trading_day + "\\" + stock_name + '_' + trading_day + "_" + trading_day + '.csv'
    try:
        stock_df = pd.read_csv(file_name)
    except:
        print("there is no file for " + stock_code + " in " + trading_day)
    else:
        stock_df.index = stock_df.time
        open_time  = trading_day + " 09:30:00"
        stock_df = stock_df[stock_df.index > open_time]
    return stock_df


def get_pre_close_price_stock(stock_code, trading_day):
    """
    得到上一日股票的收盘价
    :param stock_code:
    :param trading_day:
    :return:
    """
    pre_trading_day = get_pre_trading_day_stock(trading_day)
    df_table = get_stock_df(stock_code, pre_trading_day, pre_trading_day)
    pre_close_price = df_table.CLOSE.values[0]
    return pre_close_price


def change_trading_day_format(trading_day):
    """
    将期货格式中的trading_day转化为股票中的日期格式
    """
    trading_day_str = trading_day[:4] + '-' + trading_day[4:6] + '-' + trading_day[6:8]
    return trading_day_str


def change_trading_day_date(trading_day):
    """
    将字符串格式的trading_day转化成通过stock_df中的time格式
    :param trading_day:"20180706"
    :return: date(2018,07, 06)
    """
    trading_day_date = date(int(trading_day[:4]), int(trading_day[4:6]), int(trading_day[6:8]))
    return trading_day_date


def change_trading_day_date_stock(trading_day):
    """
    将股票的日期的字符串格式转化成stock_df中的time格式
    :param trading_day: "2018-07-06"
    :return:
    """
    trading_day_list = trading_day.split('-')
    trading_day_date = date(int(trading_day_list[0]), int(trading_day_list[1]), int(trading_day_list[2]))
    return trading_day_date


def chang_time_to_str(trading_time):
    """
    将df中格式的time格式转化为str格式
    :param trading_time:
    :return:
    """
    trading_day = str(trading_time.year) + '-' + str(trading_time.month) + '-' + str(trading_time.day)
    return trading_day


def get_all_stock_code_list(trading_day):
    """
    获取当天所有的股票代码
    """
    stock_df = retrieve_table('stock_db', 'daily_price_tb', 'time', trading_day, trading_day)
    raw_stock_code_list = stock_df.code.unique()
    stock_code_list = delete_new_stock(raw_stock_code_list, 60, trading_day)
    return stock_code_list


def drop_duplicate_index(independent_value):
    """
    将具有重复index的series去掉
    :param independent_value:
    :return:
    """
    duplicate_value = independent_value[independent_value.index.duplicated()]
    new_independent_value = independent_value.drop(duplicate_value.index)
    return new_independent_value


def find_bottom_stock(trading_day):
    """
    找出当前股价在底部的股票，筛选条件：当前股价在过去一年的价格处于20%以下的位置
    :param trading_day:
    :return:
    """
    start_date = get_next_trading_day_stock(trading_day, -260)
    sql = 'SELECT * FROM stock_db.daily_price_tb WHERE time  >= \"{start_date}\" AND time ' \
          ' <=  \"{end_date}\"'.format(start_date=start_date, end_date=trading_day)
    tp_table = fetchall_sql(sql)
    data_df = pd.DataFrame(list(tp_table))
    data_df.columns = retrieve_column_name('stock_db', 'daily_price_tb')

    year = int(trading_day.split('-')[0])
    month = int(trading_day.split('-')[1])
    days = int(trading_day.split('-')[-1])
    now_date = date(year, month, days)

    data_df['net_value'] = data_df.groupby('code')['PCT_CHG'].apply(lambda x: (x + 1).cumprod())
    data_df['rolling_high'] = data_df.groupby('code')['net_value'].apply(lambda x: x.rolling(window=252).max())
    data_df['rolling_low'] = data_df.groupby('code')['net_value'].apply(lambda x: x.rolling(window=252).min())
    data_df['value_ratio'] = (data_df['net_value'] - data_df['rolling_low']) / (
                data_df['rolling_high'] - data_df['rolling_low'])
    select_df = data_df[data_df['time'] == now_date]
    select_df = select_df[select_df['value_ratio'] < 0.2]
    bottom_stock_list = list(select_df.code)
    return bottom_stock_list


def fetch_stock_share(stock_code, trading_day):
    """
    获取股票的总股本，流通A股等因素；
    :param stock_code:
    :param trading_day:
    :return:
    """
    sql_sentence = 'SELECT * FROM stock_db.stock_num_tb where time = \"{trading_day}\" and code = \"{stock_code}\"' \
        .format(trading_day=trading_day, stock_code=stock_code)
    tp_table = fetchall_sql(sql_sentence)
    df_table = pd.DataFrame(list(tp_table), columns=['time', 'code', 'TOTAL_SHARES', 'FREE_FLOAT_SHARES', 'FLOAT_A_SHARES', 'SHARE_RESTRICTEDA'])
    total_share = df_table.TOTAL_SHARES.values[0]
    return total_share


def fetch_predict_netprofit(stock_code, trading_day):
    """
    在数据库中查找未来几年的净利润
    :param stock_code:
    :param trading_day:
    :return:
    """
    sql_sentence = 'SELECT * FROM stock_db.predict_sum_part1_tb where time = \"{trading_day}\" and code = \"{stock_code}\"' \
        .format(trading_day=trading_day, stock_code=stock_code)
    tp_table = fetchall_sql(sql_sentence)
    df_table = pd.DataFrame(list(tp_table))
    if len(df_table) > 0:
        df_table.columns = retrieve_column_name('stock_db', 'predict_sum_part1_tb')
    return df_table


def fetch_predict_roe(stock_code, trading_day):
    """
    获取每只股票的predict roe
    :param stock_code:
    :param trading_day:
    :return:
    """
    predict_roe = 0
    sql_sentence = 'SELECT * FROM stock_db.predict_sum_infor_tb where time = \"{trading_day}\" and code = \"{stock_code}\"' \
        .format(trading_day=trading_day, stock_code=stock_code)
    tp_table = fetchall_sql(sql_sentence)
    df_table = pd.DataFrame(list(tp_table))
    if len(df_table) > 0:
        df_table.columns = retrieve_column_name('stock_db', 'predict_sum_infor_tb')
        predict_roe = df_table.WEST_AVGROE_FY1.values[0]
    return predict_roe


def calc_stock_market_value(stock_code, trading_day):
    """
    根据总股本和收盘价计算出该股票的大致的市值；
    :param stock_code:
    :param trading_day:
    :return:
    """
    stock_df = get_stock_df(stock_code, trading_day, trading_day)
    close_price = stock_df.CLOSE.values[0]
    total_share = fetch_stock_share(stock_code, trading_day)
    market_value = close_price * total_share
    return market_value


def calc_stock_predict_pe(stock_code, trading_day):
    """
    计算预测的pe值，用预测盈利，和股本数，股票价格
    :param stock_code:
    :param trading_day:
    :return:
    """
    predict_pe = 0
    stock_df = get_stock_df(stock_code, trading_day, trading_day)
    close_price = stock_df.CLOSE.values[-1]
    total_share = fetch_stock_share(stock_code, trading_day)
    predict_profit_df = fetch_predict_netprofit(stock_code, trading_day)
    predict_profit_fy1 = predict_profit_df.WEST_NETPROFIT_FY1.values[0]
    if predict_profit_fy1 > 0:
        predict_pe = float(close_price * total_share) / float(predict_profit_fy1)
    return predict_pe


def get_index_stock_list(index_name, trading_day):
    """
    获取指数的成分股列表，指数有沪深300，中证500，上证50
    :param index_name:hs300, sh50, zz500;
    :param trading_day:
    :return:
    """
    sql = 'SELECT * FROM stock_db.{index_name}_tb WHERE DATE = \"{trading_day}\"'.format(index_name=index_name, trading_day=trading_day)
    tp_table = fetchall_sql(sql)
    df_table = pd.DataFrame(list(tp_table))
    df_table.columns = retrieve_column_name('stock_db', index_name + '_tb')
    constituent_df = df_table.set_index('THSCODE')
    return constituent_df


def get_index_stock_df(start_date, end_date, index_name):
    """
    获取某个指数的成分股的日线列表，沪深300，中证500，上证50；
    :param start_date:
    :param end_date:
    :param index_name:000300.SH, 000905.SH, 000016.SH
    :return:
    """
    sql = 'SELECT * FROM stock_db.daily_price_tb WHERE time  >= \"{start_date}\" AND time ' \
          ' <=  \"{end_date}\"'.format(start_date=start_date, end_date=end_date)
    tp_table = fetchall_sql(sql)
    df_table = pd.DataFrame(list(tp_table))
    df_table.columns = retrieve_column_name('stock_db', 'daily_price_tb')
    df_table = df_table[(df_table.PCT_CHG > -12) & (df_table.PCT_CHG < 12)]
    df_table = df_table.set_index('code')

    index_code = 'hs300'
    if index_name == '000300.SH':
        index_code = 'hs300'
    elif index_name == '000905.SH':
        index_code = 'zz500'
    elif index_name == '000016.SH':
        index_code = 'sh50'
    # 只考虑指数中的股票，沪深300，上证50，或者中证500
    constituent_df = get_index_stock_list(index_code, end_date)
    df_table = df_table.join(constituent_df)
    df_table = df_table.dropna(subset=['WEIGHT'])
    df_table['code'] = df_table.index
    return df_table


if __name__ == '__main__':
    # start_date = '2018-02-17'
    # end_date = '2018-02-26'
    # test = retrieve_table('stock_db', 'daily_price_tb', 'time', start_date, end_date)
    # print(test.head())
    trading_day = '2018-03-09'
    find_all_stock_concept_list(trading_day)






