# -*- coding: utf-8 -*-
"""

# 将想要选择的合约copy出来到一个指定的文件夹中

Created on Wed Dec 07 16:28:19 2016

@author: Tracy Zhu
"""
import os
import shutil

from datetime import datetime
# now = datetime.now()
# trading_day_now = now.strftime('%Y%m%d')
trading_day_now = '20180715'

variety_id_list = ["AL1809", "AL1810", "AL1811", "CU1809", "CU1810", "CU1811", "NI1811", "NI1901" , "ZN1809", "ZN1810", "ZN1811"]
trading_day_list_file_name = "F:\\tool\\base_data\\Trading_Day.txt"
trading_day_list_file = open(trading_day_list_file_name, "r")
trading_day_list = trading_day_list_file.readlines()
trading_day_list_file.close()

for trade_day in trading_day_list:
    trading_day = trade_day[:-1]
    # if trading_day > '20180529':
    if trading_day >= trading_day_now:
        for variety_id in variety_id_list:
            print trading_day, variety_id
            copy_file_folder = 'Z:\\'
            copy_file_name = copy_file_folder + trading_day + '\\' + variety_id + '.csv'

            target_file_folder = 'E:\\quote_data\\chose_instrument_id\\' + trading_day + '\\'
            isExists = os.path.exists(target_file_folder)
            if not isExists:
                os.makedirs(target_file_folder)

            shutil.copy(copy_file_name, target_file_folder)

