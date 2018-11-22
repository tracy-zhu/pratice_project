# -*- coding: utf-8 -*-
"""

# 本文件包含了一些处理数据中一开始常用的方法

Tue 2016/10/11

@author: Tracy Zhu
"""
from python_base.constant import *
from pandas import DataFrame, Series
from datetime import datetime
from datetime import timedelta
from sklearn import linear_model
from collections import defaultdict
# from python_base.Line_Text_To_Best_Marketdata import *
# from python_base.Quote_File_Manage import *

import pandas as pd
import numpy as np
import xml.dom.minidom
import os
import statsmodels.api as sm
import seaborn as sns


# ----------------------------------------------------------------------
# 这里的trading_day输入的是字符串
def get_trade_phase(trading_day):
    for dirpath, dirnames, filenames in os.walk(G_TRADE_PHASE_FOLDER):
        for name in filenames:
            if int(name[0:8]) <= int(trading_day) <= int(name[9:17]):
                trade_phase_file = G_TRADE_PHASE_FOLDER + "\\" + name
                return trade_phase_file


# ----------------------------------------------------------------------
def get_variety_id(instrument_name):
    variety_id = instrument_name[0]
    if "A" <= instrument_name[1] <= "Z":
        variety_id = variety_id + instrument_name[1]
    return variety_id


# ----------------------------------------------------------------------
def get_variety_information(variety_id):
    root = G_DOM.documentElement
    itemlist = root.getElementsByTagName('VarietyPhase')
    for item in itemlist:
        if variety_id == item.getAttribute("varietyid").encode("gbk"):
            tick = float(item.getAttribute("tick").encode("gbk"))
            unit = float(item.getAttribute("unit").encode("gbk"))
            exchtype = float(item.getAttribute("exchtype").encode("gbk"))
            if exchtype == 1:
                exchange_id = "CFFEX"
            else:
                exchange_id = "OTHER"
            return tick, unit, exchange_id


# ----------------------------------------------------------------------
def get_opentime(variety_id, trade_phase_file):
    dom = xml.dom.minidom.parse(trade_phase_file)
    root = dom.documentElement
    itemlist = root.getElementsByTagName('VarietyPhase')
    for item in itemlist:
        if variety_id == item.getAttribute("varietyid").encode("gbk"):
            open_time = item.getAttribute("opentime").encode("gbk")
            open_time = open_time + ':00'
            return open_time


# ----------------------------------------------------------------------
def get_phase_time(variety_id, trade_phase_file):
    end_time_list = []
    begin_time_list = []
    dom = xml.dom.minidom.parse(trade_phase_file)
    root = dom.documentElement
    itemlist = root.getElementsByTagName('VarietyPhase')
    for item in itemlist:
        if variety_id == item.getAttribute("varietyid").encode("gbk"):
            phase_time_list = item.getElementsByTagName('Phase')
            for phase_time in phase_time_list:
                end_time = phase_time.getAttribute("endtime").encode("gbk")
                end_time_list.append(end_time)
                begin_time = phase_time.getAttribute("begintime").encode("gbk")
                begin_time_list.append(begin_time)
    zip_phase_time = zip(begin_time_list, end_time_list)
    return zip_phase_time 


# ----------------------------------------------------------------------
def get_instrument_file_list(trading_day):
    folder_path = G_TICK_QUOTE_FILE_ROOT_FOLDER + "\\" + trading_day
    if folder_path is None:
        raise Exception("folder_path is None")

    # 获取该交易日的文件列表
    instrument_file_list = defaultdict(list)
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for name in filenames:
            if 6 < len(name) < 11 and "A" <= name[0] <= "Z":
                variety_id = get_variety_id(name)
                instrument_file_list[variety_id].append(dirpath + '\\' + name)
        return instrument_file_list

# ----------------------------------------------------------------------
# change the index of DataFrame to combination of UpdateTime and Update_Millisec
def get_dataframe(data, frequency):
    Update_Millisec_str = []
    stamp_index = []
    trading_day_list = []
    trading_day = str(int(data.Trading_Day.values[-1]))
    pre_trading_day = get_pre_trading_day(trading_day)
    data = data.dropna(subset=['Update_Time'], how='any')
    for values in data.Update_Millisec:
        str_values = str(values).zfill(3)
        Update_Millisec_str.append(str_values)
    for update_time in data.Update_Time:
        if int(update_time.split(":")[0]) > 15:
            trading_day_list.append(str(int(pre_trading_day)))
        else:
            trading_day_list.append(str(int(trading_day)))
    time_index = data.Update_Time + "." + Update_Millisec_str + " " + trading_day_list
    for temp_time in time_index:
        stamp = datetime.strptime(temp_time, '%H:%M:%S.%f %Y%m%d')
        stamp_index.append(stamp)
    DF_data = DataFrame(data.values, index=stamp_index, columns=G_TICK_COLUMNS)
    resample_data = DF_data.resample(frequency).first()
    resample_data = resample_data.dropna(how='all')
    trading_day = trading_day_list[0]
    year = int(trading_day[:4])
    month = int(trading_day[4:6])
    day = int(trading_day[6:8])
    night_resample_data =  resample_data[resample_data.index >= datetime(year,month,day,21,0,0)]
    day_resample_data = resample_data[resample_data.index <= datetime(year,month,day,15,0,0)]
    concat_resample_data = pd.concat([night_resample_data, day_resample_data])
    return concat_resample_data


# ----------------------------------------------------------------------
def read_data(instrument_id, trading_day):
    quote_data = DataFrame()
    file_name = G_TICK_QUOTE_FILE_ROOT_FOLDER + "\\" + trading_day + "\\" + instrument_id + ".csv"
    try:
        f = open(file_name, "r")
    except IOError:
        str_line = "there is no file for " + instrument_id + " in " + trading_day
        print(str_line)
    else:
        f.close()
        quote_data = pd.read_csv(file_name, header=0, index_col=False, names=G_TICK_COLUMNS)
        variety_id = get_variety_id(instrument_id)
        open_time = get_opentime(variety_id, TRADE_PHASE_FILE_NAME)
        open_index = quote_data.index[quote_data.Update_Time >= open_time]
        if len(open_index) > 0:
            open_index = open_index[0]
        else:
            open_index = 0
        quote_data = quote_data[quote_data.index >= open_index]
    return quote_data


# ----------------------------------------------------------------------
# 与上面简单的read_data不同的是，这里将index换成了时间序列，便于后面数据的对齐
def read_data_with_time_index(instrument_id, trading_day):
    DF_data = DataFrame()
    file_name = G_TICK_QUOTE_FILE_ROOT_FOLDER + "\\" + trading_day + "\\" + instrument_id + ".csv"
    try:
        f = open(file_name, "r")
    except IOError:
        str_line = "there is no file for " + instrument_id + " in " + trading_day
        print (str_line)
    else:
        f.close()
        quote_data = pd.read_csv(file_name, header=0, index_col=False, names=G_TICK_COLUMNS)
        variety_id = get_variety_id(instrument_id)
        open_time = get_opentime(variety_id, TRADE_PHASE_FILE_NAME)
        open_index = quote_data.index[quote_data.Update_Time >= open_time]
        if len(open_index) > 0:
            open_index = open_index[0]
        else:
            open_index = 0
        quote_data = quote_data[quote_data.index >= open_index]
        Update_Millisec_str = []
        stamp_index = []
        trading_day_list = []
        trading_day = str(int(quote_data.Trading_Day.values[0]))
        pre_trading_day = get_pre_trading_day(trading_day)
        data = quote_data.dropna(subset=['Update_Time'], how='any')
        for values in data.Update_Millisec:
            str_values = str(values).zfill(3)
            Update_Millisec_str.append(str_values)
        for update_time in data.Update_Time:
            if int(update_time.split(":")[0]) > 15:
                trading_day_list.append(str(int(pre_trading_day)))
            else:
                trading_day_list.append(str(int(trading_day)))
        time_index = data.Update_Time + "." + Update_Millisec_str + " " + trading_day_list
        for temp_time in time_index:
            stamp = datetime.strptime(temp_time, '%H:%M:%S.%f %Y%m%d')
            stamp_index.append(stamp)
        DF_data = DataFrame(data.values, index=stamp_index, columns=G_TICK_COLUMNS)
    return DF_data


# ----------------------------------------------------------------------
def get_time_index(quote_data):
    """
    根据quote_data，生成datetime格式的index序列
    :param quote_data:
    :return:
    """
    Update_Millisec_str = []
    stamp_index = []
    trading_day_list = []
    trading_day = str(int(quote_data.Trading_Day.values[0]))
    pre_trading_day = get_pre_trading_day(trading_day)
    data = quote_data.dropna(subset=['Update_Time'], how='any')
    for values in data.Update_Millisec:
        str_values = None
        if values == 0 or values == 500:
            str_values = str(values).zfill(3)
        elif 0 < values < 500:
            str_values = '000'
        elif 500 < values < 1000 :
            str_values = '500'
        Update_Millisec_str.append(str_values)
    for update_time in data.Update_Time:
        if int(update_time.split(":")[0]) > 15:
            trading_day_list.append(str(int(pre_trading_day)))
        else:
            trading_day_list.append(str(int(trading_day)))
    time_index = data.Update_Time + "." + Update_Millisec_str + " " + trading_day_list
    for temp_time in time_index:
        stamp = datetime.strptime(temp_time, '%H:%M:%S.%f %Y%m%d')
        stamp_index.append(stamp)
    return stamp_index


# ----------------------------------------------------------------------
# 读取降维的数据
def get_low_dimension_data(instrument_id, trading_day, frequency):
    quote_data = read_data(instrument_id, trading_day)
    open_index = quote_data.index[0]
    quote_data = quote_data[quote_data.index > open_index]
    quote_data = quote_data.dropna(axis=0, subset=['Trading_Day'])
    end_index = quote_data[quote_data.Update_Time <= "15:00:00"].index[-1]
    quote_data = quote_data[quote_data.index <= end_index]
    resample_data = get_dataframe(quote_data, frequency)
    return resample_data

# ----------------------------------------------------------------------
# 读取一分钟数据文件
def read_minute_data(instrument_id, trading_day):
    file_name = ONE_MINUTE_QUOTE_FILE_FOLDER + "\\" + trading_day + "\\" + instrument_id + ".csv"
    quote_data = pd.read_csv(file_name, header=0, index_col=False, names=MINUTE_COLUMNS)
    return quote_data


# ----------------------------------------------------------------------
def get_main_instrument_id(instrument_list):
    quote_map = {}
    if len(instrument_list) > 2:
        for one_file_name in instrument_list:
            quote_file = open(one_file_name, "r")
            quote_list = quote_file.readlines()
            quote_file.close()
            instrument_id = one_file_name.split("\\")[-1].split(".")[0]
            close_quote = CBest_Market_Data_Field()
            if len(quote_list) > 2000:
                if len(quote_list[-1]) > 2:
                    close_quote = Get_CBest_Market_Data_Field_From_Line(quote_list[-1])
                else:
                    close_quote = Get_CBest_Market_Data_Field_From_Line(quote_list[-2])
                quote_map[instrument_id] = close_quote
            else:
                close_quote = CBest_Market_Data_Field()
                close_quote.Total_Match_Volume = 10
                quote_map[instrument_id] = close_quote


        # 寻找主力合约
        if len(quote_map) > 2:
            # 寻找主力合约
            best_quote_frame = Series()
            for (instrument_id, close_quote) in quote_map.items():
                best_quote = Series([instrument_id, close_quote.Total_Match_Volume])
                best_quote_frame = best_quote_frame.append(best_quote)
            best_quote_frame = Series(best_quote_frame[1].values, index=best_quote_frame[0].values)
            best_quote_frame_sort = best_quote_frame.sort_values()
            main_instrument_id = best_quote_frame_sort.index[-1]
            sub_instrument_id = best_quote_frame_sort.index[-2]
            if quote_map[main_instrument_id].Total_Match_Volume > LIMIT_TRADE_VOLUME:
                return main_instrument_id, sub_instrument_id
            else:
                print ("Can't find the correct instrument")
                return None, None
    else:
        return None, None

# ----------------------------------------------------------------------
# 根据品种名称和交易日获取当天的主力合约
def get_variety_main(variety_id, trading_day):
    instrument_file_list = get_instrument_file_list(trading_day)
    instrument_list = instrument_file_list[variety_id]
    main_instrument_id, sub_instrument_id = get_main_instrument_id(instrument_list)
    return main_instrument_id, sub_instrument_id


# ----------------------------------------------------------------------
# 获取某个时间的第一笔行情最新价
def get_price_on_time(quote_data, node_time):
    node_price = None
    node_price_series = quote_data[quote_data.Update_Time == node_time]
    if len(node_price_series) > 0:
        node_price = node_price_series.Last_Price.values[0]
    else:
        for i in range(1, 10):
            node_time_new = node_time[:-1] + str(i)
            if len(quote_data[quote_data.Update_Time == node_time_new]) > 0:
                node_price = quote_data[quote_data.Update_Time == node_time_new].Last_Price.values[0]
                break
    return node_price


# ----------------------------------------------------------------------
# 获取某个时间的第一笔行情切片
def get_slice_quote_on_time(quote_data, node_time):
    slice_quote = Series()
    node_price_series = quote_data[quote_data.Update_Time == node_time]
    if len(node_price_series) > 0:
        slice_quote = node_price_series.loc[node_price_series.index[0]]
    else:
        for i in range(1, 10):
            node_time_new = node_time[:-1] + str(i)
            if len(quote_data[quote_data.Update_Time == node_time_new]) > 0:
                node_price_series = quote_data[quote_data.Update_Time == node_time_new]
                slice_quote = node_price_series.loc[node_price_series.index[0]]
                break
    return slice_quote


# ----------------------------------------------------------------------
# 输入是一DataFrame，每一列是一支股票在每一日的价格
def find_cointegration_pairs(dataframe):
    # 得到DataFrame长度
    n = dataframe.shape[1]
    # 初始化p值矩阵
    pvalue_matrix = np.ones((n, n))
    # 抽取列的名称
    keys = dataframe.keys()
    # 初始化强协整组
    pairs = []
    # 对于每一个i
    for i in range(n):
        # 对于大于i的j
        for j in range(i+1, n):
            # 获取相应的两只股票的价格Series
            stock1 = dataframe[keys[i]]
            stock2 = dataframe[keys[j]]
            # 分析它们的协整关系
            result = sm.tsa.stattools.coint(stock1, stock2)
            # 取出并记录p值
            pvalue = result[1]
            pvalue_matrix[i, j] = pvalue
            # 如果p值小于0.05
            if pvalue < 0.05:
                # 记录股票对和相应的p值
                pairs.append((keys[i], keys[j], pvalue))
    # 返回结果
    return pvalue_matrix, pairs

# ----------------------------------------------------------------------
def zscore(series):
    return (series - series.mean()) / np.std(series)

# ----------------------------------------------------------------------
# 获取文件列表
def get_trading_day_list():
    trading_day_list_file = open(TRADING_DAY_LIST_FILE_NAME, "r")
    trading_day_list = trading_day_list_file.readlines()
    trading_day_list_file.close()
    return trading_day_list

# ----------------------------------------------------------------------
# 获取每天的收盘价
def get_close_price(instrument_id, trading_day):
    one_file_name = G_TICK_QUOTE_FILE_ROOT_FOLDER + "\\" + trading_day + "\\" + instrument_id + ".csv"
    quote_file = open(one_file_name, "r")
    quote_list = quote_file.readlines()
    quote_file.close()
    close_quote = CBest_Market_Data_Field()
    if len(quote_list) > 2000:
        if len(quote_list[-1]) > 2:
            close_quote = Get_CBest_Market_Data_Field_From_Line(quote_list[-1])
        else:
            close_quote = Get_CBest_Market_Data_Field_From_Line(quote_list[-2])

        return close_quote.Last_Price

# ----------------------------------------------------------------------
# 获取每天的开盘价
def get_open_price_from_quote_data(instrument_id, trading_day):
    open_price = None
    open_time = '20:59:00'
    quote_data = read_data(instrument_id, trading_day)
    main_open_quote = quote_data[quote_data.Update_Time == open_time]
    if len(main_open_quote) > 0:
        open_price = main_open_quote.Last_Price.values[0]
    return open_price

# ----------------------------------------------------------------------
# 以下两个函数计算两个品种之间的线性回归分析
def get_data(x_series, y_series):
    X_parameter = []
    Y_parameter = []
    for single_square_feet, single_price_value in zip(x_series, y_series):
        X_parameter.append([float(single_square_feet)])
        Y_parameter.append(float(single_price_value))
    return X_parameter, Y_parameter


def linear_model_main(X_parameters, Y_parameters, predict_value):
    # Create linear regression object
    regr = linear_model.LinearRegression()
    regr.fit(X_parameters, Y_parameters)
    predict_outcome = regr.predict(predict_value)
    predictions = dict()
    predictions['intercept'] = regr.intercept_
    predictions['coefficient'] = regr.coef_
    predictions['predicted_value'] = predict_outcome
    return predictions

# ----------------------------------------------------------------------
# 函数得到下午三点到夜盘开盘前该品种外盘的变化,如果没有该品种的当天的变化则显示为0
out_change_data = pd.read_csv(OUTER_DATA_CHANGE_FILE_NAME, header=0, index_col=False, names=DATA_CHANGE_COLUMNS)
def get_outer_data_change(instrument_id, trading_day):
    change_ratio = 0
    variety_id = get_variety_id(instrument_id)
    out_change_data_by_day = out_change_data[out_change_data.Quote_Day == int(trading_day)]
    if variety_id in out_change_data_by_day.Influence_Variety_Name.values:
        out_change_data_by_variety = out_change_data_by_day[out_change_data_by_day.Influence_Variety_Name == variety_id]
        change_ratio = out_change_data_by_variety.Change_Ratio.values[0]
    return change_ratio

# ----------------------------------------------------------------------
# 根据当个交易日计算前一个交易日的交易日期
def get_pre_trading_day(trading_day):
    # now_trading_day = datetime.strptime(trading_day, '%Y%m%d')
    # if now_trading_day.weekday() == 0:
    #     yesterday = now_trading_day - timedelta(days=3)
    #     pre_trading_day = yesterday.strftime('%Y%m%d')
    # else:
    #     yesterday = now_trading_day - timedelta(days=1)
    #     pre_trading_day = yesterday.strftime('%Y%m%d')
    trading_day_list = get_trading_day_list()
    trading_day_index = trading_day_list.index(trading_day+'\n')
    pre_trading_day = trading_day_list[trading_day_index - 1][:-1]
    return pre_trading_day

# ----------------------------------------------------------------------
# 根据当个交易日股票计算前一个交易日的交易日期
def get_pre_trading_day_stock(trading_day):
    "股票日期格式为2018=03-05"
    trading_day_list = get_trading_day_list()
    trading_day = ''.join(trading_day.split("-"))
    trading_day_index = trading_day_list.index(trading_day+'\n')
    pre_trading_day = trading_day_list[trading_day_index - 1][:-1]
    pre_trading_day = pre_trading_day[:4] + '-' + pre_trading_day[4:6] + '-' + pre_trading_day[6:8]
    return pre_trading_day


def change_day_str_stock(trading_day):
    """
    接受期货格式的trading_day, 转化为"2018-03-05"
    :param trading_day: 20180305
    :return:
    """
    change_day = trading_day[:4] + '-' + trading_day[4:6] + '-' + trading_day[6:8]
    return change_day

# ----------------------------------------------------------------------
# 根据当个交易日股票后n个交易日的交易日期
def get_next_trading_day(trading_day, holding_days):
    global trading_day_list
    end_date = None
    trading_day_list = get_trading_day_list()
    trading_day_index = trading_day_list.index(trading_day+'\n')
    if (trading_day_index + holding_days) < len(trading_day_list):
        end_date = trading_day_list[trading_day_index + holding_days][:-1]
    else:
        end_date = trading_day_list[-1]
    return end_date

if __name__ == '__main__':
    instrument_id = 'RB1801'
    result_file = 'open_and_close_price.txt'
    f = open(result_file, 'wb')
    trading_day_list = get_trading_day_list()
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        if trading_day > '20170814':
            open_price = get_open_price_from_quote_data(instrument_id, trading_day)
            close_price = get_close_price(instrument_id, trading_day)
            print>>(f, trading_day, ',', open_price, ',', close_price)
    # instrument_file_list = get_instrument_file_list(trading_day)
    # for variety, instrument_list in instrument_file_list.items():
    #     main_instrument_id, _ = get_main_instrument_id(instrument_list)
    #     if main_instrument_id != None:
    #         print main_instrument_id
    #         f.write(main_instrument_id+ "\n")

    f.close()