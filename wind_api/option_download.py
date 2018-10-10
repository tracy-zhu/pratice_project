# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 09:14:58 2018

@author: Tracy Zhu
"""
from WindPy import w

import sys

# 导入用户库：
sys.path.append("..")
out_file_folder = "..\\wind_api\\picture\\"
from python_base.plot_method import *


def download_data_wind(start_date, end_date, var_list):
    if w.isconnected() == False:
        w.start()
    raw = w.wsi(var_list, "open, high, low, close, volume, amt",start_date, end_date, "")
    raw_df = pd.DataFrame(raw.Data, index=raw.Fields, columns=raw.Times)
    raw_df = raw_df.T
    return raw_df


def out_to_csv(var_value):
    pass


if __name__ == '__main__':
    start_date = "2018-02-22 09:00:00"
    end_date = "2018-02-27 15:00:00"
    var_list = ["10001173.SH", "10001174.SH", "10001148", "10001143"]

