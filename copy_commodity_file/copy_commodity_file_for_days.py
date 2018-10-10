# -*- coding: utf-8 -*-
"""
Created on Wed Dec 07 16:28:19 2016

@author: Tracy Zhu
"""
import os
import shutil

from datetime import datetime
now = datetime.now()
# trading_day = now.strftime('%Y%m%d')
# trading_day = '20161013'

trading_day_list_file_name = "F:\\tool\\base_data\\Trading_Day.txt"
trading_day_list_file = open(trading_day_list_file_name, "r")
trading_day_list = trading_day_list_file.readlines()
trading_day_list_file.close()

for trade_day in trading_day_list:
    trading_day = trade_day[:-1]
    if trading_day > '20170208':
        copy_file_folder = 'Y:\\'
        copy_file_name = copy_file_folder + trading_day + '\\' + trading_day + '_GSMN_155.7z'

        target_file_folder = 'E:\\quote_data\\commodity_data_SR\\' + trading_day + '\\'
        isExists = os.path.exists(target_file_folder)
        if not isExists:
                os.makedirs(target_file_folder)
                
        shutil.copy(copy_file_name, target_file_folder)

        target_file_name = target_file_folder + trading_day + '_GSMN_155.7z'

        os.chdir(target_file_folder)
        command_line =  'D:\\software\\7-Zip\\7z x \"' + target_file_name + '\" -y -aos -o\"' + target_file_folder + '\"'
        os.system(command_line)

        del_command = 'del ' +  target_file_name
        os.system(del_command)
