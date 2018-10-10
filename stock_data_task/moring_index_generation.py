# -*- coding: utf-8 -*-
"""

# 生成每天晨会需要查看的市场情绪指标；生成到当天的文件夹中

# 在大盘下跌的过程中显得比较重要

Thu 2018/03/15

@author: Tracy Zhu
"""

# 导入系统库
import sys

# 导入用户库
sys.path.append("..")
from wind_api.sql_download import *

start_date = '20171005'
now = datetime.now()
end_date = now.strftime('%Y%m%d')


out_file_folder = 'D:\\strategy\\open_price_strategy\\stock_data\\emotion_index\\' + end_date + "\\"
isExists = os.path.exists(out_file_folder)
if not isExists:
    os.makedirs(out_file_folder)

conn = connect_data_source()
turnover_rate_and_total_match_volume(conn, start_date, end_date, out_file_folder)
