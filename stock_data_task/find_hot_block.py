# -*- coding: utf-8 -*-
"""

# 生成当天板块中，涨的股票中占比比较高的板块，及板块整体涨幅较大

# 然后在从热点板块中确定比较好的股票

Tue 2018/03/20

@author: Tracy Zhu
"""

# 导入系统库
import sys
import codecs
from iFinDPy import *

# 导入用户库
sys.path.append("..")
from stock_data_task.up_limit_strength_sort import *

THS_iFinDLogin('tbtz035', '834909')

out_file_folder = "D:\\strategy\\open_price_strategy\\stock_data\\hot_block\\"


def stock_list_description(stock_code_list, trading_day, spot_time):
    """
    根据股票代码和交易日找出当天这个股票池的涨跌幅比例，平均涨跌幅
    :param stock_code_list:
    :param trading_day:
    :return:
    """
    block_yield_mean = -999
    positive_ratio = -999
    positive_ratio_change = -999
    stock_default_dict = defaultdict()
    percent_chg_list = []
    positive_num = 0
    spot_positive_num = 0
    trading_day_str = ''.join(trading_day.split('-'))
    for stock_code in stock_code_list:
        print stock_code
        try:
            # stock_df = get_stock_df(stock_code, trading_day, trading_day)
            stock_tick_data = read_stock_tick_data(stock_code, trading_day_str)
        except:
            print "stock code is wrong!"
        else:
            # percent_chg = stock_df['PCT_CHG'].values[0]
            if len(stock_tick_data) > 0:
                close_price = stock_tick_data.lastPrice.values[0]
                pre_close_price = stock_tick_data.preClosePrice.values[0]
                percent_chg = (float(close_price) / float(pre_close_price) - 1) * 100
                spot_yield_value = get_spot_time_price(stock_code, trading_day, spot_time)
                if percent_chg > -12 and percent_chg < 12:
                    stock_default_dict[stock_code] = percent_chg
                    percent_chg_list.append(percent_chg)
                if percent_chg > 0:
                    positive_num += 1
                if spot_yield_value > 0:
                    spot_positive_num += 1
        if len(percent_chg_list) > 0:
            block_yield_mean = Series(percent_chg_list).mean()
            positive_ratio = float(positive_num) / float(len(percent_chg_list))
            spot_positive_ratio = float(spot_positive_num)/ float(len(percent_chg_list))
            positive_ratio_change = positive_ratio - spot_positive_ratio
    return block_yield_mean, positive_ratio, positive_ratio_change


def find_leading_stock_by_iwencai(block_name):
    """
    同过iwencai的行情接口找出板块中主力资金流向/平均成交金额 排名靠前的股票
    :param concept_name:
    :return:
    """
    select_code_str = ''
    query_sentence = u'主力资金流向/3天的区间日成交金额 ' + block_name.decode('utf-8')
    result = THS_iwencai(query_sentence, 'stock')
    try:
        result_table = result['tables'][0]['table']#[u'股票代码']
        ratio_values = result_table[result_table.keys()[4]]
        select_code_list = result_table[result_table.keys()[0]]
    except:
        print 'something is wrong!'
    else:
        stock_dict = defaultdict()
        for index in range(len(select_code_list)):
            stock_code = select_code_list[index]
            ratio_value = ratio_values[index]
            stock_dict[stock_code] = ratio_value
        sorted_dict = sorted(stock_dict.items(), key=lambda d: d[1], reverse=True)
        select_code = list(zip(*sorted_dict[:3])[0])
        select_code_str = ','.join(select_code)
    return select_code_str


def find_leading_stock(stock_code_list, trading_day):
    """
    找出选出的股票优先涨停的，这样找出龙1，龙2，龙3
    :param stock_code_list:
    :return:
    """
    pass


def get_spot_time_price(stock_code, trading_day, spot_time):
    """
    获取指定日期的指定时间的股票的收盘价，目的是为了获得该板块2:30的涨幅，和收盘的涨幅作比较
    找出比较大的部分；
    :param stock_code:
    :param trading_day:
    :param spot_time:'14:30'
    :return:
    """
    yield_value = -999
    trading_day_str = ''.join(trading_day.split('-'))
    # minute_data = read_stock_minute_data(stock_code, trading_day)
    # index_time = trading_day + ' ' + spot_time
    # df_table = minute_data[minute_data.index >= index_time]
    # pre_close_price = get_pre_close_price_stock(stock_code, trading_day)
    tick_data = read_stock_tick_data(stock_code, trading_day_str)
    if len(tick_data) > 0:
        df_table = tick_data[tick_data.index >= 143000]
        if len(df_table) > 0:
            spot_price = df_table.lastPrice.values[0]
            pre_close_price = df_table.preClosePrice.values[0]
            yield_value = float(spot_price) / float(pre_close_price) - 1
    return yield_value


if __name__ == '__main__':
    now = datetime.now()
    trading_day = now.strftime('%Y-%m-%d')
    # trading_day = '2018-03-20'
    day_folder = out_file_folder + trading_day + "\\"

    isExists = os.path.exists(day_folder)
    if not isExists:
        os.makedirs(day_folder)

    pre_trading_day = get_pre_trading_day_stock(trading_day)
    spot_time = '14:30'
    block_code_list = find_all_stock_concept_list_ifind(pre_trading_day)

    block_default_dict = defaultdict()
    last_hour_change_dict = defaultdict()
    for block_code in block_code_list:
        concept_code = block_code.split(',')[0]
        stock_code_list = find_concept_stock_ifind(concept_code, pre_trading_day)
        block_yield_mean, positive_ratio, positive_ratio_change = stock_list_description(stock_code_list, trading_day, spot_time)
        block_default_dict[block_code] = (block_yield_mean, positive_ratio)
        last_hour_change_dict[block_code] = (block_yield_mean, positive_ratio_change)

    sorted_block_by_ratio = sorted(block_default_dict.items(), key=lambda d: d[1][1], reverse=True)
    sorted_block_by_last_half_ratio = sorted(last_hour_change_dict.items(), key=lambda d: d[1][1], reverse=True)

    file_name = day_folder + 'hot_block.csv'
    f = open(file_name, 'wb')
    f.write(codecs.BOM_UTF8) # 防止乱码
    for values in sorted_block_by_ratio[:20]:
        block_name = values[0].split(',')[1]
        select_code_str = find_leading_stock_by_iwencai(block_name)
        positive_ratio = values[1][1]
        print >>f,  block_name, ',', positive_ratio, ",", select_code_str

    f.close()

    file_name_2 = day_folder + 'half_hour_change.csv'

    f2 = open(file_name_2, 'wb')
    f2.write(codecs.BOM_UTF8) # 防止乱码
    for values2 in sorted_block_by_last_half_ratio[:20]:
        block_name = values2[0].split(',')[1]
        select_code_str = find_leading_stock_by_iwencai(block_name)
        positive_ratio = values2[1][1]
        print>>f2,  block_name, ',', positive_ratio, ",", select_code_str
    f2.close()
