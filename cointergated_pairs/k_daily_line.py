# coding: utf-8

import MySQLdb
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statsmodels.formula.api as smf
import seaborn as sns
from pylab import *
from pandas import DataFrame, Series
import os
import pandas as pd
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

sys.path.append('..')
from python_base.common_method import *
trading_day_list = get_trading_day_list()

mpl.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
mpl.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题


database_ip = "10.47.102.126"

def get_k_daily_data_from_database(instrument_id):
    # 连接数据库
    con = MySQLdb.connect(host=database_ip, user="root", passwd="123456", port=3306, db="info1", local_infile=1,
                          charset='gbk')
    cursor = con.cursor()
    command = "select trading_day, close_price from daily_k_data_test where instrument_id = \'%s\' order by trading_day" % instrument_id
    cursor.execute(command)

    con.commit()
    data_get = cursor.fetchall()
    con.close()
    return data_get

def transfer_data_get_to_series(instrument_id):
    price_data_list = get_k_daily_data_from_database(instrument_id)

    unzip_data_list = map(list, zip(*price_data_list))
    trading_day_list = unzip_data_list[0]
    price_list = unzip_data_list[1]

    price_series = Series(price_list, index=trading_day_list)
    price_series = price_series[price_series != 0]
    return price_series

def get_close_price_series(instrument_id, start_date, end_date):
    index_trading_day_list = []
    close_price_list = []
    for trade_day in trading_day_list:
        trading_day = trade_day[:-1]
        if start_date <= trading_day <= end_date:
            index_trading_day_list.append(trading_day)
            close_price = get_close_price(instrument_id, trading_day)
            close_price_list.append(close_price)
    price_series = Series(close_price_list, index=index_trading_day_list)
    price_series = price_series[price_series != 0]
    return price_series


def draw(id_1, id_2):
    # price_series_1 = transfer_data_get_to_series(id_1)
    # price_series_2 = transfer_data_get_to_series(id_2)

    start_date = '20170101'
    end_date = '20170509'
    price_series_1 = get_close_price_series(id_1, start_date, end_date)
    price_series_2 = get_close_price_series(id_2, start_date, end_date)


    x_list = price_series_2.keys()
    price_list_1 = price_series_1.values
    price_list_2 = price_series_2.values


    x_length = len(x_list)
    if x_length <= 50:
        times_delta = 1
    elif x_length <= 90:
        times_delta = 3
    else:
        times_delta = 4
    # 处理横坐标的标签
    group_labels = []
    i = 0
    for index in range(x_length):
        if i % times_delta == 0:
            group_labels.append(x_list[index])
        else:
            group_labels.append('')
        i += 1

    # xy标签
    plt.xlabel(u"日期")
    plt.ylabel(u"价格")
    # 标题
    title11 = id_1 + ' and ' + id_2 + u"的价格曲线"
    plt.title(title11)

    x_list_last = range(0, len(price_list_1))

    # group_labels = x_list

    plt.plot(x_list_last, price_list_1, 'b', linewidth=0.5)
    plt.plot(x_list_last, price_list_2, 'r', linewidth=0.5)

    plt.legend([id_1, id_2], loc='best')

    # 横坐标设置(坐标代替,倾斜度)
    plt.xticks(x_list_last, group_labels, rotation=30)
    # 网格线
    plt.grid()

    now_path = os.getcwd()
    # print now_path
    save_pic_path = now_path + '\\picture'
    try:
        os.mkdir(save_pic_path)
    except:
        pass
    save_pic_name = save_pic_path + '\\' + id_1 + '_k_line' + '.jpg'
    savefig(save_pic_name)

    plt.show()


def linear_model_main(price_series_1, price_series_2):
    X = price_series_2
    result = (sm.OLS(price_series_1, X)).fit()
    # constant_para = result.params.const
    coef_para = result.params.X_data
    Z_data = price_series_1 - price_series_2 * coef_para 
    print(result.summary())
    return Z_data
    

def linear_model_main_with_intercept(price_series_1, price_series_2):
    X = sm.add_constant(price_series_2)
    result = (sm.OLS(price_series_1, X)).fit()
    constant_para = result.params.const
    coef_para = result.params.X_data
    Z_data = price_series_1 - price_series_2 * coef_para - constant_para
    print(result.summary())
    return Z_data


def ecm_model_main(price_series_1, price_series_2, Z_data, lag_num):
    duration_num = len(price_series_1) - lag_num
    delta_y_data = price_series_1.diff()
    delta_x_data = price_series_2.diff()
    delta_z_data = Z_data.diff()
    linear_model_dict = {}
    linear_model_dict = {"delta_x_t":delta_x_data.values[(1+lag_num):duration_num+lag_num], "delta_x_pre_t":delta_x_data.values[1:duration_num],
                         "delta_y_t":delta_y_data.values[(1+lag_num):duration_num+lag_num], "delta_y_pre_t":delta_y_data.values[1:duration_num],
                         "delta_z_pre_t":delta_z_data.values[1:duration_num]}
    linear_model_dataframe = DataFrame(linear_model_dict)
    mod_x = smf.ols(formula='delta_x_t~delta_x_pre_t + delta_y_pre_t + delta_z_pre_t', data=linear_model_dataframe)
    mod_y = smf.ols(formula='delta_y_t~delta_x_pre_t + delta_y_pre_t + delta_z_pre_t', data=linear_model_dataframe)
    result_x = mod_x.fit()
    result_y = mod_y.fit()
    print(result_x.summary())
    print(result_y.summary())


def judge_if_cointegrated(price_series_1, price_series_2):
    result = sm.tsa.stattools.coint(price_series_1, price_series_2)
    p_value = result[1]
    if p_value < 0.05:
        print "is cointegrated! and p_value is " + str(p_value)
    else:
        print "not cointegrated! and p_value is" + str(p_value)


if __name__ == '__main__':
    id_1 = 'ZC709'
    id_2 = 'JM1709'
    start_date = '20170120'
    end_date = '20170824'
    price_series_1 = get_close_price_series(id_1, start_date, end_date)
    price_series_2 = get_close_price_series(id_2, start_date, end_date)
    # draw(id_1, id_2)
    
    # price_series_1 = transfer_data_get_to_series(id_1)
    # price_series_2 = transfer_data_get_to_series(id_2)
    concat_data_frame = pd.concat([price_series_1, price_series_2], axis=1)
    concat_data_frame = concat_data_frame.dropna()
    price_series_1 = Series(concat_data_frame[0], name='Y_data')
    price_series_2 = Series(concat_data_frame[1], name='X_data')
    judge_if_cointegrated(price_series_1, price_series_2)
    Z_data = linear_model_main(price_series_1, price_series_2)
    #Z_data = linear_model_main_with_intercept(price_series_1, price_series_2)
    print Z_data.std()
    # ecm_model_main(price_series_1, price_series_2, Z_data, 1)
    fig = plt.figure()
    fig.set_size_inches(23.2, 14.0)
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(Z_data.values)



