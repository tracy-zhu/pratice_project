# -*- coding: utf-8 -*-
"""

# 每天计算期权的三个PCR指标，对大盘做判断

Fri 2018/11/01

@author: Tracy Zhu
"""

import sys

# 导入用户库
sys.path.append("..")
from stock_base.stock_option_base import *
from python_base.plot_method import *


def calc_pcr_by_daily_data_ths(trading_day):
    """
    根据数据库生成的期权日线数据，计算每天的put call ratio,包括成交量的，持仓量的和成交额的
    :param trading_day:
    :return:
    """
    position_pcr = 0
    amount_pcr = 0
    volume_pcr = 0
    option_daily_df = read_option_data_daily_ths(trading_day)
    call_option_df = option_daily_df[option_daily_df.ths_delta_option > 0]
    put_option_df = option_daily_df[option_daily_df.ths_delta_option < 0]
    volume_call_num = call_option_df.ths_vol_option.sum()
    volume_put_num = put_option_df.ths_vol_option.sum()
    amount_call_num = call_option_df.ths_amt_option.sum()
    amount_put_num = put_option_df.ths_amt_option.sum()
    position_call_num = call_option_df.ths_open_interest_option.sum()
    position_put_num = put_option_df.ths_open_interest_option.sum()
    if position_call_num > 0 and amount_call_num > 0 and volume_call_num > 0:
        position_pcr = float(position_put_num) / float(position_call_num)
        amount_pcr = float(amount_put_num) / float(amount_call_num)
        volume_pcr = float(volume_put_num) / float(volume_call_num)
    print('position pcr is ' + str(position_pcr))
    print('amount pcr is ' + str(amount_pcr))
    print('volume pcr is ' + str(volume_pcr))
    return position_pcr, amount_pcr, volume_pcr


if __name__ == '__main__':
    trading_day = '2018-11-21'
    # now = datetime.now()
    # trading_day = now.strftime('%Y-%m-%d')
    print(trading_day)
    result = calc_pcr_by_daily_data_ths(trading_day)


