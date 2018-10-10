# -*- coding: utf-8 -*-
"""

# 对尾盘策略的进行回测；

# 主要的纠结点在于板块的龙头股的确定；

Tue 2018/04/02

@author: Tracy Zhu
"""

# 导入系统库
import sys

# 导入用户库
sys.path.append("..")
from stock_data_task.find_hot_block import *
from stock_base.stock_file_api import *

picture_out_folder = ".\\stock_backtest\\picture\\"
trading_day_list = get_trading_day_list()


def get_select_stock_by_late_day(trading_day):
    """
    首先根据分钟数据筛选出当日的热点板块，在从热点板块中找到龙头股票
    :param trading_day:'2018-03-02"
    :return:
    """
    select_code_list = []
    sorted_block_by_last_half_ratio, block_stock_dict = get_hot_block_late_day(trading_day)
    for block_code_item in sorted_block_by_last_half_ratio[:3]:
        block_code = block_code_item[0]
        # print block_code
        sorted_stock_list = block_stock_dict[block_code]
        for stock_code, values in sorted_stock_list:
            pct_chg  = values[0]
            if pct_chg < 0.09:
                select_code_list.append(stock_code)
                # print stock_code
                break
    return select_code_list


def get_hot_block_late_day(trading_day):
    """
    根据盘后最后一段时间的筛选出排序的热点板块
    :param trading_day:'2018-03-02'
    :return:
    """
    pre_trading_day = get_pre_trading_day_stock(trading_day)
    spot_time = '14:30'
    block_code_list = find_all_stock_concept_list_ifind('2018-03-30')

    block_stock_dict = defaultdict()
    last_hour_change_dict = defaultdict()
    for block_code in block_code_list:
        concept_code = block_code.split(',')[0]
        stock_code_list = find_concept_stock_ifind(concept_code, '2018-03-30')
        positive_ratio, positive_ratio_change, sorted_stock_list = block_describe_find_leading_stock(stock_code_list, trading_day, spot_time)
        last_hour_change_dict[block_code] = (positive_ratio, positive_ratio_change)
        block_stock_dict[block_code] = sorted_stock_list

    sorted_block_by_last_half_ratio = sorted(last_hour_change_dict.items(), key=lambda d: d[1][1], reverse=True)
    return sorted_block_by_last_half_ratio, block_stock_dict


def block_describe_find_leading_stock(stock_code_list, trading_day, spot_time):
    """
    对每个板块的半小时变化进行排序，并找出其中的龙头股票。先按照涨跌幅进行排名,每个板块取前3只股票
    :param stock_code:
    :param trading_day:
    :param spot_time:
    :return:
    """
    positive_ratio = -999
    positive_ratio_change = -999
    stock_default_dict = defaultdict()
    percent_chg_list = []
    positive_num = 0
    spot_positive_num = 0
    for stock_code in stock_code_list:
        print stock_code
        spot_yield, percent_chg, close_price = get_stock_slice_data_by_minute_data(stock_code, trading_day, spot_time)
        if percent_chg > -12 and percent_chg < 12:
            stock_default_dict[stock_code] = (percent_chg, close_price)
            percent_chg_list.append(percent_chg)
            if percent_chg > 0:
                positive_num += 1
            if spot_yield > 0:
                spot_positive_num += 1
        if len(percent_chg_list) > 0:
            positive_ratio = float(positive_num) / float(len(percent_chg_list))
            spot_positive_ratio = float(spot_positive_num)/ float(len(percent_chg_list))
            positive_ratio_change = positive_ratio - spot_positive_ratio
    sorted_stock_list = sorted(stock_default_dict.items(), key=lambda d: d[1][0], reverse=True)[:5]
    return  positive_ratio, positive_ratio_change, sorted_stock_list


def get_stock_after_trend(stock_code, trading_day):
    """
    得出选出的股票的后期走势，取后面10个交易日的走势，开仓价格选出当天的收盘价
    :param select_code_list:
    :param trading_day:
    :return:
    """
    holding_days = 10
    end_date = get_next_trading_day_stock(trading_day, holding_days)
    df_table = get_stock_df(stock_code, trading_day, end_date)
    pct_series = df_table.CLOSE / df_table.CLOSE.values[0] - 1
    return pct_series


def get_block_after_trend(block_stock_code_list, trading_day):
    """
    计算板块后面几天的收益率，看其分布
    :param block_code:
    :param trading_day:"2018-04-3"
    :return:
    """
    holding_days = 10
    end_date = get_next_trading_day_stock(trading_day, holding_days)
    stock_yield_dict = defaultdict()
    for stock_code, values in block_stock_code_list:
        pct_series = get_stock_after_trend(stock_code, trading_day)
        stock_yield_dict[stock_code] = pct_series
    stock_yield_df = DataFrame(stock_yield_dict)
    pct_series = stock_yield_df.mean(axis=1)
    index_df = get_index_data("000300.SH", trading_day, end_date)
    index_yield = index_df['pct_chg'].sum()
    pct_series = pct_series - index_yield / 100
    return pct_series


def get_hot_block_after_trend(trading_day):
    """
    首先根据前面最后半小时的筛选指标和热点板块，然后得出前三个热点板块
    得出后面板块的走势
    :param trading_day:"2018-04-03"
    :return:
    """
    pct_series_list = []
    sorted_block_by_last_half_ratio, block_stock_dict = get_hot_block_late_day(trading_day)
    for block_code_item in sorted_block_by_last_half_ratio[:3]:
        block_code = block_code_item[0]
        # print block_code
        block_stock_code_list = block_stock_dict[block_code]
        pct_series = get_block_after_trend(block_stock_code_list, trading_day)
        pct_series_list.append(pct_series)
    return pct_series_list


def yield_distribution_after_trend_plot(stock_pct_df):
    """
    将后期每天的收益率分布绘制出来
    :param stock_pct_df: dataframe, 是后面每一天的收益率分布
    :return:
    """
    global picture_out_folder
    for index in stock_pct_df.index[1:]:
        yield_distribution = stock_pct_df.loc[index]
        yield_distribution = yield_distribution[yield_distribution > -1]
        fig, ax = plt.subplots()
        plt.hist(yield_distribution)
        title = 'distribution of ' + str(index) + ' days'
        fig.set_size_inches(23.2, 14.0)
        plt.title(title)
        out_file_name = picture_out_folder + title + '.png'
        plt.savefig(out_file_name)


if __name__ == '__main__':
    start_date = '20171129'
    end_date = '20180406'
    block_pct_dict1 = defaultdict()
    block_pct_dict2 = defaultdict()
    block_pct_dict3 = defaultdict()
    count_num = 1
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        if trading_day >= start_date and trading_day <= end_date:
            trading_day_str = change_trading_day_format(trading_day)
            pct_series_list = get_hot_block_after_trend(trading_day_str)
            block_pct_dict1[count_num] = pct_series_list[0]
            block_pct_dict2[count_num] = pct_series_list[1]
            block_pct_dict3[count_num] = pct_series_list[2]
            count_num += 1
    block_pct_df1 = DataFrame(block_pct_dict1)
    block_pct_df2 = DataFrame(block_pct_dict2)
    block_pct_df3 = DataFrame(block_pct_dict3)
    yield_distribution_after_trend_plot(block_pct_df3)

    #         select_code_list = get_select_stock_by_late_day(trading_day_str)
    #         # for stock_code in select_code_list:
    #         stock_code1 = select_code_list[0]
    #         pct_series1 = get_stock_after_trend(stock_code1, trading_day_str)
    #         stock_pct_dict1[count_num] = pct_series1
    #         if len(select_code_list) > 1:
    #             stock_code2 = select_code_list[1]
    #             pct_series2 = get_stock_after_trend(stock_code2, trading_day_str)
    #             stock_pct_dict2[count_num] = pct_series2
    #         count_num += 1
    # stock_pct_df = DataFrame(stock_pct_dict1)
    # stock_pct_df1 = DataFrame(stock_pct_dict1)
    # stock_pct_df2 = DataFrame(stock_pct_dict2)
    # yield_distribution_after_trend_plot(stock_pct_df2)



