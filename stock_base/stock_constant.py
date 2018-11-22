# encoding: UTF-8
# 该文件用来保存股票常量

# 股票分钟数据
stock_minute_file_path =  "V:\\raw_data\\minutes_data\\"

# 股票tick数据目录
stock_tick_file_path = "V:\\qdam_rt_data\\"
# 钱哥接收的tick行情数据，相对比较稳定
stock_tick_file_path_qian = "V:\\snapdata_ths\\"
# 50期权tick数据目录，同花顺新
option_tick_file_path_ths = "V:\\snapdata_fo_ths\\"
# 50期权tick数据目录，wind旧
option_tick_file_path = "V:\\snapdata_fo\\"

# 股票实时行情数据， 钱哥
wind_rt_data_path = "V:\\wind_rt_data\\"
rt_data_columns = ['index_code', "update_time", "amount", "pct_chg", "last_price", "ask_price1", 'bid_price1',
                   'bid_volume1', 'ask_volume1', 'wp_values', 'np_values']

# wind概念指数中不需要的指数，如国家队指数，融资融券指数；
delete_concept_list_wind = ['884196.WI', '884198.WI', '884240.WI', '884242.WI', '884245.WI', '884257.WI', '884059.WI',
                            '8841101.W', '8841112.W']

# 程序参考
# import codecs
# f.write(codecs.BOM_UTF8) # 防止中文输入到csv乱码
