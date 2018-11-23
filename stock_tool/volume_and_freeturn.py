# -*- coding: utf-8 -*-
"""

# 从数据库读入每天的上证指数的换手率和成交量

Tue 2018/11/20

@author: Tracy Zhu
"""

# 导入系统库
import sys

# 导入用户库
sys.path.append("..")
from stock_base.stock_backtest_function import *
from python_base.plot_method import *


now = datetime.now()
end_date = now.strftime('%Y-%m-%d')

index_code = '000001.SH'
start_date = '2017-01-01'
index_df = get_index_data(index_code, start_date, end_date)

out_file_folder = "D:\\strategy\\open_price_strategy\\stock_data\\emotion_index\\" + end_date + "\\"

isExists = os.path.exists(out_file_folder)
if not isExists:
    os.mkdir(out_file_folder)
out_file_name = out_file_folder + "index_amt_and_freeturn.png"

fig, ax = plt.subplots()
ax.plot(index_df['amt'], color='r', label="index amt")
ax1 = ax.twinx()
# ax1.plot(oil_df['SPG_shift'], color="b", label="SPG shift")
ax1.plot(index_df['free_turn'], color="b", label="index free turn")
ax.legend(loc="upper left")
ax1.legend(loc="upper right")
title = "index amt and free_turn"
plt.title(title)
fig.set_size_inches(23.2, 14.0)
plt.savefig(out_file_name)
