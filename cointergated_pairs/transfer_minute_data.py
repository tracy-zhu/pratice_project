# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 14:49:45 2017

# 每天将分钟数据转换出来

@author: Tracy Zhu
"""

import os
from datetime import datetime
import time

now = datetime.now()
trading_day = now.strftime('%Y%m%d')
#trading_day = "20170914"
os.chdir("F:\\quot_tools")
int_hour = time.localtime().tm_hour

command_line = ''
if int_hour > 15:
    command_line = "quote_tools_minute Z:\\" + trading_day + " E:\\quote_data\\1M_K 1"
else:
    command_line = "quote_tools_minute Z:\\night_data\\" + trading_day + " E:\\quote_data\\1M_K 1"
#command_line = "quote_tools_minute V:\\night_data\\"+ trading_day + " E:\\quote_data\\1M_K 1"
os.system(command_line)
