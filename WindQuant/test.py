# -*- coding: utf-8 -*-
from WindPy import *
import pandas as pd
from collections import defaultdict
import math
import pandas as pd

w.start()

end_date = '2018-08-27'
start_date = '2017-01-01'
list_A = w.wset("SectorConstituent",u"date=20180827;sector=全部A股").Data[1] 
indicator_name = "mfd_netbuyamt"
position_num = 3


def prepare_raw_data(start_date, trading_day):
    global indicator_name
    model_date = w.tdays(start_date, trading_day, "").Data[0]
    model_date_list = [j.strftime('%Y-%m-%d') for j in model_date]
    data_model_buy = w.wsd(list_A, indicator_name, start_date, trading_day, "traderType=1")
    data_model_buy = pd.DataFrame(data_model_buy.Data, index=data_model_buy.Codes, columns=data_model_buy.Times)
    data_model_buy.columns = model_date_list
    industry_df = get_stock_industry()
    data_model_buy["indexcode_sw"] = industry_df
    buy_money_sum = data_model_buy.groupby('indexcode_sw').sum().T
    return buy_money_sum
    

def get_stock_industry():
    industry_df = w.wss(list_A, "indexcode_sw", "tradeDate=20180827;industryType=2")
    industry_df = pd.DataFrame(industry_df.Data, columns=industry_df.Codes, index=industry_df.Fields).T
    return industry_df


def calc_cash_indicator(index_series):
    data_df = pd.DataFrame()
    data_df['rolling_money'] = index_series.rolling(window=10).mean()
    data_df['rolling_money'] = index_series.shift(1)
    data_df['cash_money'] = index_series
    data_df['money_ratio'] =  data_df['cash_money'] / data_df['rolling_money']
    #money_ratio = data_df['money_ratio'].values[-1]
    return data_df['money_ratio']
    

def get_indicator_df(buy_money_sum):
    indicator_dict = defaultdict()
    for columns_name in buy_money_sum.columns:
        index_series = buy_money_sum[columns_name]
        money_ratio_series = calc_cash_indicator(index_series)
        indicator_dict[columns_name] = money_ratio_series
    indicator_df = pd.DataFrame(indicator_dict)
    return indicator_df
    

def get_position_list(indicator_df, position_num):
    position_dict = dict()
    for trading_day in indicator_df.index:
        position_list = []
        sort_indicator = indicator_df.ix[trading_day].sort_values(ascending=False)
        for index in sort_indicator.index:
            if len(position_list) <= position_num - 1:
                if not math.isinf(sort_indicator.ix[index]):
                    position_list.append(index)
            continue
        position_dict[trading_day] = position_list
    return position_dict


def get_position_list_by_days(start_date, trading_day):
    global position_num
    buy_money_sum = prepare_raw_data(start_date, trading_day)
    indicator_df = get_indicator_df(buy_money_sum)
    position_dict = get_position_list(indicator_df, position_num)
    return position_dict


def calc_all_position_dict(start_date, end_date):
    all_position_dict = dict()
    step_num = 100
    model_date = w.tdays(start_date, end_date, "").Data[0]
    model_date_list = [j.strftime('%Y-%m-%d') for j in model_date]
    begin_step = 0
    end_step = begin_step + step_num
    end_time = 0
    while end_time != end_date:
        begin_time = model_date_list[begin_step]
        end_time = model_date_list[end_step]
        print(begin_time)
        if end_time >= end_date:
            end_time = end_date
        position_dict = get_position_list_by_days(begin_time, end_time)
        begin_step = end_step + 1
        end_step = begin_step + step_num
        all_position_dict = dict(all_position_dict, **position_dict)
    return all_position_dict

all_position_dict = calc_all_position_dict(start_date, end_date) 
