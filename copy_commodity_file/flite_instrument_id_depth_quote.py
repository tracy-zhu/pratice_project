# -*- coding: utf-8 -*-
"""

# 将想要选择的深度合约copy出来到一个指定的文件夹中

Created on Wed Dec 07 16:28:19 2016

@author: Tracy Zhu
"""
import os
import shutil

from datetime import datetime
now = datetime.now()
# trading_day = now.strftime('%Y%m%d')
# trading_day = '20161013'

variety_id_list = ['RB1801', "RB1805", 'RB1810']
trading_day_list_file_name = "F:\\tool\\base_data\\Trading_Day.txt"
trading_day_list_file = open(trading_day_list_file_name, "r")
trading_day_list = trading_day_list_file.readlines()
trading_day_list_file.close()

for trade_day in trading_day_list:
    trading_day = trade_day[:-1]
    if trading_day > '20171130':
        for variety_id in variety_id_list:
            print trading_day, variety_id
            copy_file_folder = 'W:\\'
            copy_file_name = copy_file_folder + trading_day + '\\' + variety_id + '.txt'

            target_file_folder = 'E:\\quote_data\\chose_instrument_id_depth\\' + trading_day + '\\'
            isExists = os.path.exists(target_file_folder)
            if not isExists:
                os.makedirs(target_file_folder)
            try:
                f = open(copy_file_name, 'r')
            except:
                print "can't find the file " + copy_file_name
            else:
                f.close()
                shutil.copy(copy_file_name, target_file_folder)