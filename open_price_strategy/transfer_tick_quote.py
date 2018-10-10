# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 14:49:45 2017

# 该脚本用于集合竞价的深度行情展示

@author: Tracy Zhu
"""

from python_base.constant import *
to_deal_folder = "C:\\Users\\Tracy Zhu\\Desktop\\test_for_open_price\\tick_quote.csv"
result_file = "C:\\Users\\Tracy Zhu\\Desktop\\test_for_open_price\\tick_quote_new.csv"

to_deal_file = open(to_deal_folder, "r")
out_file = open(result_file, "wb")
all_lines = to_deal_file.readlines()

for index in range(len(all_lines)):
    str_line = all_lines[index]
    if index == 0:
        out_file.write(str_line)
    else:
        str_line_list = str_line.split(',')
        update_time = str_line_list[1]
        new_update_time = "".join(update_time.split(":")) + "00"
        new_line = ",".join(str_line_list[:-1]) + "," + new_update_time + '\n'
        print update_time
        out_file.write(new_line)

to_deal_file.close()
out_file.close()

# for str_line in all_lines:
#     str_line_list = str_line.split(',')
#     print len(str_line_list)
#     print str_line_list
#     print len(G_TICK_COLUMNS)
#     break