# -*- coding: utf-8 -*-
"""

# 输出高频策略需要的相关性和波动率文件；

Tue 2018/07/10

@author: Tracy Zhu
"""

# 导入系统库
import sys

# 导入用户库
sys.path.append("..")
from future_market_maker.correlation_matrix import *
from future_market_maker.volatility_generation import *

out_file_folder = '..\\future_market_maker\\result\\'

frequency = "5min"
period = 10
# trading_date = datetime.now()
# end_date = trading_date.strftime('%Y%m%d')
end_date = "20180720"

yield_dict = defaultdict()
instrument_id_list = ["J1809", "JM1809", "RB1810", "RB1901"]
# instrument_id_list = ["JM1805", "J1805", "I1805", "RB1805", "RB1810", "HC1805", "T1806", "TF1806"]
for instrument_id in instrument_id_list:
    print instrument_id
    vwap_yield = get_days_vwap_yield(instrument_id, end_date, frequency, period)
    yield_dict[instrument_id] = vwap_yield

yield_data_frame = DataFrame(yield_dict)
yield_data_frame = yield_data_frame.dropna(how="all")
result = yield_data_frame.corr()
variety_id_list = []
for instrument_id in result.index:
    variety_id_list.append(get_variety_id(instrument_id))
result = DataFrame(result.values, index=result.index, columns=result.index)
correlation_result = result[instrument_id_list]
correlation_result = correlation_result.reindex(instrument_id_list)


volatility_dict = defaultdict()

for instrument_id in instrument_id_list:
    total_vwap_yield = get_days_vwap_yield(instrument_id, end_date, frequency, period)
    annualized_volatility = get_realized_volatility(total_vwap_yield, period)
    volatility_dict[instrument_id] = annualized_volatility
    print instrument_id, annualized_volatility

volatility_series = Series(volatility_dict)

correlation_result['volatility'] = volatility_series
correlation_result = correlation_result.reindex(instrument_id_list)

print correlation_result

out_file_name = "..\\future_market_maker\\result\\correlation_and_volatility.csv"
correlation_result.to_csv(out_file_name)