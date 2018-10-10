# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 14:49:45 2017

# 该脚本用于统计资金情绪指标和某个期货品种收益率的关系

@author: Tracy Zhu
"""

# 导入系统库
import sys
import scipy.stats as st

# 导入用户库
sys.path.append("..")
from python_base.plot_method import *
variety_id = 'T'
result_file_name = "E:\\quote_data\\pang_data\\capital_sentiment_index.xlsx"

result_data = pd.read_excel(result_file_name)
node_1 = '09:15:00'
node_2 = '10:15:00'
node_3 = '14:30:00'

capital_sentiment_index_list = []
yield_list = []

def get_period_yield_by_trading_day(trading_day):
    instrument_file_list = get_instrument_file_list(trading_day)
    instrument_list = instrument_file_list[variety_id]
    main_instrument_id, _ = get_main_instrument_id(instrument_list)
    quote_data = read_data(main_instrument_id, trading_day)
    node_1_price = get_price_on_time(quote_data, node_1)
    node_2_price = get_price_on_time(quote_data, node_2)
    node_3_price = get_price_on_time(quote_data, node_3)
    close_price = get_close_price(main_instrument_id, trading_day)
    period_1_yield = (node_2_price - node_1_price) / node_1_price
    period_2_yield = (node_3_price - node_2_price) / node_2_price
    period_3_yield = (close_price - node_3_price) / node_3_price
    period_day_list = [period_1_yield, period_2_yield, period_3_yield]
    return period_day_list


def linear_model_main_without_intercept(price_series_1, price_series_2):
    X = price_series_2
    result = (sm.OLS(price_series_1, X)).fit()
    # constant_para = result.params.const
    coef_para = result.params.X_data
    Z_data = price_series_1 - price_series_2 * coef_para  # - constant_para
    print(result.summary())
    return Z_data


for index in result_data.index:
    trading_day = result_data.date[index].strftime('%Y%m%d')
    print trading_day
    period_day_yield_list = get_period_yield_by_trading_day(trading_day)
    yield_list = yield_list + period_day_yield_list
    period_1_index = result_data[845][index]
    period_2_index = result_data[1015][index]
    period_3_index = result_data[1430][index]
    period_index_list = [period_1_index, period_2_index, period_3_index]
    capital_sentiment_index_list = capital_sentiment_index_list + period_index_list

cor, pval = st.pearsonr(capital_sentiment_index_list, yield_list)

capital_sentiment_index_series = Series(capital_sentiment_index_list, name='X_data')
yield_series = Series(yield_list, name='Y_data')
linear_model_main_without_intercept(yield_series, capital_sentiment_index_series)
standard_capital_sentiment_index_series = zscore(capital_sentiment_index_series)
standard_yield_series = zscore(yield_series)

standard_capital_sentiment_index_series.plot()
standard_yield_series.plot()
