# -*- coding: utf-8 -*-
"""

# 脚本用于将深度行情转化成10档或者5档的行情

Tue 2017/3/14

@author: Tracy Zhu
"""
# 导入系统库
import os
from datetime import datetime


source_file_folder = "E:\\quote_data\\depth_quote_after_auction\\"
out_file_folder = "E:\\quote_data\\five_level_depth_quote\\"
now = datetime.now()
# trading_day = now.strftime('%Y%m%d')
trading_day = '20170705'
depth_level = 5

# 将深度行情文件转化为计算的行情文件
def generate_depth_quote(to_deal_file, out_file_name):
    mbl_quote_file = open(to_deal_file, "r")
    out_file = open(out_file_name, "wb")
    all_lines = mbl_quote_file.readlines()
    mbl_quote_file.close()

    for deal_line in all_lines:
        deal_line_list = deal_line.split(',')
        incise_num = depth_level * 2 + 2
        incise_line_list = deal_line_list[:incise_num]
        incise_line = ",".join(incise_line_list) + '\n'
        out_file.write(incise_line)
    out_file.close()


if __name__ == '__main__':
    day_file_folder = source_file_folder + trading_day + "\\"
    out_day_file_folder = out_file_folder + trading_day + "\\"
    if not os.path.exists(out_day_file_folder):
        os.makedirs(out_day_file_folder)
    for son_dir_path, son_dir_names, son_filenames in os.walk(day_file_folder):
        for file_name in son_filenames:
            if len(file_name) > 9:
                to_deal_file = day_file_folder + file_name
                out_file_name = out_day_file_folder + file_name
                print_line = file_name[:-4] + " in " + str(trading_day)
                print print_line
                generate_depth_quote(to_deal_file, out_file_name)
    
