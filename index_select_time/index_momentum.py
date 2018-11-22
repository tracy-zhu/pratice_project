# -*- coding: utf-8 -*-
"""

# 计算沪深300或者其他宽基指数是否存在动量或者反转效应

# 首先从最简单的,前一个月为正，则做多，否则空仓，按周调仓；


Tue 2018/11/06

@author: Tracy Zhu
"""

# 导入系统库
import sys

# 导入用户库
sys.path.append("..")
from stock_base.stock_data_api import *
from python_base.plot_method import *


def parameter_init():
    # 生成回测必要的参数
    parameter_dict = defaultdict()
    parameter_dict['start_date'] = '2016-01-01'
    parameter_dict['end_date'] = '2018-11-09'
    parameter_dict['back_period'] = 10
    parameter_dict['holding_period'] = 30
    parameter_dict['index_name'] = 'zz500'
    return parameter_dict


def index_momentum_test(parameter_dict):
    """
    根据回测的参数，计算大盘的动量效应有多明显；
    :param parameter_dict:
    :return:
    """
    pass


