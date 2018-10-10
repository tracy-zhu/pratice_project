# encoding: UTF-8
# 该文件用来保存股票常量

# 股票分钟数据
stock_minute_file_path =  "V:\\raw_data\\minutes_data\\"

# 股票tick数据目录
stock_tick_file_path = "V:\\qdam_rt_data\\"
# 钱哥接收的tick行情数据，相对比较稳定
stock_tick_file_path_qian = "V:\\snapdata\\"

# 股票实时行情数据， 钱哥
wind_rt_data_path = "V:\\wind_rt_data\\"
rt_data_columns = ['index_code', "update_time", "amount", "pct_chg", "last_price", "ask_price1", 'bid_price1',
                   'bid_volume1', 'ask_volume1', 'wp_values', 'np_values']

# 程序参考
# import codecs
# f.write(codecs.BOM_UTF8) # 防止中文输入到csv乱码
