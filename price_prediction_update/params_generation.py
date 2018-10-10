# -*- coding: utf-8 -*-
"""

# 生成李老师策略所需要参数，生成csv文件

Wed 2018/4/25

@author: Tracy Zhu
"""
# 导入系统库
import sys

# 导入用户库：
sys.path.append("..")
from intercommodity_prediction_update import *

trading_day = "20180423"
out_file_folder = "..\\price_prediction_update\\params_folder\\"
out_file_name = out_file_folder + "params.csv"
f = open(out_file_name, 'wb')


instrument_id_group = ["RB1805", "RB1810", "JM1809", "J1809"]
for dependent_instrument_id in instrument_id_group:
    # dependent_instrument_id = "RB1805"
    print dependent_instrument_id
    forecast_num = 20
    # independent_instrument_list = get_independent_instrument(instrument_id_group, dependent_instrument_id)
    params_series = intercommodity_prediction_update(dependent_instrument_id, instrument_id_group, trading_day, forecast_num)
    str_line = (',').join(params_series.astype('str')) + '\n'
    f.write(str_line)

f.close()
