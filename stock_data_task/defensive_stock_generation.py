# -*- coding: utf-8 -*-
"""

# 每天生成最近三天，收益率最高的前50只股票代码名称和收益率

# 在大盘下跌的过程中显得比较重要

Thu 2018/03/15

@author: Tracy Zhu
"""

# 导入系统库
import sys
import codecs

# 导入用户库
sys.path.append("..")
from stock_tool.find_defensive_stock import *

out_file_folder = "D:\\strategy\\open_price_strategy\\stock_data\\defensive_stock\\"

# now = datetime.now()
# end_date = now.strftime('%Y-%m-%d')
end_date = '2018-09-07'
# start_date = get_next_trading_day_stock(end_date, -60)
start_date = '2018-08-28'

file_folder = out_file_folder + end_date
isExists = os.path.exists(file_folder)
if not isExists:
    os.makedirs(file_folder)


def print_stock_out(stock_df, file_name):
    """
    将筛选出的股票输出到一个文件夹中，股票代码，当天的收益率
    :param stock_df:
    :param file_name:
    :return:
    """
    global file_folder, end_date
    out_file_name = file_folder + "\\" + file_name
    f = open(out_file_name, 'wb')
    f.write(codecs.BOM_UTF8) # 防止乱码
    for stock_code in stock_df.index:
        print stock_code
        chi_name = find_stock_chi_name(stock_code)
        df_table = get_stock_df(stock_code, end_date, end_date)
        pct_chg = df_table.PCT_CHG.values[0]
        print >>f, stock_code, ',', chi_name, ',', str(pct_chg)
    f.close()


free_turn_sort, stock_volume_sort = volume_ratio_stock_sort(start_date, end_date)
free_file_name = "free_turn_sort.csv"
volume_ratio_file_name = "volume_ratio_sort.csv"
print_stock_out(free_turn_sort, free_file_name)
print_stock_out(stock_volume_sort, volume_ratio_file_name)


# out_file_name = file_folder + "\\defensive_stock_data.txt"
# select_code_list, stock_change_sort = find_defensive_stock(start_date, end_date, 50)

out_file_name = file_folder + "\\defensive_stock_data_without_high_volatility.txt"
select_code_list, stock_change_sort = find_defensive_stock_without_high_volatility(start_date, end_date, 50)
select_code_df = stock_change_sort.head(50)
f = open(out_file_name, 'wb')

for stock_code in select_code_df.index:
    yield_value = select_code_df.loc[stock_code]
    chi_name = find_stock_chi_name(stock_code)
    print>>f, stock_code, ",", chi_name, ',', str(yield_value)

f.close()
