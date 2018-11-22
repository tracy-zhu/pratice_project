# -*- coding: utf-8 -*-
"""

# 根据参数寻优，画出热力图，找出最稳定的参数；
# 首先参数寻优的rsrs策略

Mon 2018/09/03

@author: Tracy Zhu
"""

import sys

# 导入用户库
sys.path.append("..")
from techiniacl_analysis_stock.rsrs_research import *


start_date = '2008-01-01'
end_date = '2018-11-12'
S = 0.7
context = Context(start_date, end_date, S)
N_list = range(10, 40)
M_list = range(100, 400, 20)
data = get_index_data("000905.SH", start_date, end_date)
data = data[['time', 'code', 'open', 'high', 'low', 'close']]
data.rename(columns={'time': 'tradeday', 'code': 'sec_code', 'open': 'open_slice', 'high': 'high_slice',
                     'low': 'low_slice', 'close': 'close_slice'}, inplace=True)
data['trade_dir'] = -1

return_dict = dict()
sharpe_dict = dict()
drawback_dict = dict()
for N in N_list:
    for M in M_list:
        print(M, N)
        data_ind = RSRS(data, N, M, S=0.7, ndays=5)
        data_ind = data_ind[data_ind.sec_code == '000905.SH']
        indicator_series = Series(data_ind['rsrs_std_cor_right'].values, index=data_ind.tradeday)
        indicator_series = indicator_series.dropna()
        context = Context(start_date, end_date, S)
        holding_cumprod_pct, index_cumprod_pct, total_fee = back_test_by_indicator(indicator_series, context)
        annulized_return, sharpe_ratio, max_drowback = calc_evaluation_index(holding_cumprod_pct)
        return_dict[N, M] = annulized_return
        sharpe_dict[N, M] = sharpe_ratio
        drawback_dict[N, M] = max_drowback


def convert_dict_df(temp_dict):
    "将上述变成的dict转化成df"
    res_df = pd.DataFrame(temp_dict, index=[0]).T.reset_index()
    res_df.columns = ['N', 'M', 'return']
    res_mat = res_df.set_index(['N', 'M'])['return'].unstack()
    res_mat = res_mat.T
    return res_mat

res_mat = convert_dict_df(return_dict)
drawback_mat = convert_dict_df(drawback_dict)
sharpe_mat = convert_dict_df(sharpe_dict)
cmap = sns.color_palette("RdBu_r", 40)
fig = plt.figure(figsize=(12, 8))
ax2 = plt.subplot(111)
sns.heatmap(res_mat, yticklabels=True, annot=True, cmap=cmap, linecolor='black', linewidths=0.05, ax=ax2, cbar=True)
# ax2.set_title(ths_time)
plt.yticks(rotation=0)
#
plt.savefig('./plot1/' + 'heatmap_try22.png')