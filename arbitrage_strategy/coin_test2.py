# coding:utf-8

import pandas as pd
from pylab import *
import numpy as np
import seaborn as sns
import talib

"""

首先取得铜2个合约的数据转化成numpy的数组格式

然后作协整分析

"""

### 工作准备
###
# 文件路径
file_path = "Z:\\"


def get_data(date_start, date_end, instrument_id_1, instrument_id_2, set_ma, short_ma, set_std):
    price_delta_list = []
    price_delta_data_frame_list= []

    # 持仓标志
    flag = 0
    # 盈利
    e_l_tot = 0
    # 成交次数
    times = 0

    for date in range(date_start, date_end+1):
        print date, set_ma, set_std
        csv_path_1 = file_path + str(date) + '\\' + instrument_id_1 + '.csv'
        csv_path_2 = file_path + str(date) + '\\' + instrument_id_2 + '.csv'

        try:
            f1 = pd.DataFrame(pd.read_csv(csv_path_1), columns=['Update_Time', 'Last_Price', 'Bid_Price1', 'Ask_Price1'])
            f2 = pd.DataFrame(pd.read_csv(csv_path_2), columns=['Update_Time', 'Last_Price', 'Bid_Price1', 'Ask_Price1'])
        except:
            continue

        # 次主力上一笔的价格
        last_price_second_main = 0
        # 次主力上一笔买价
        last_bid_price_second_main = 0
        # 次主力上一笔卖价
        last_ask_price_second_main = 0

        ###得到每日行情数据，逐笔推送
        for i in range(1, f1.index[-1]):
            update_time = f1.iloc[i]['Update_Time']
            update_time_mi = f1.iloc[i]['Update_Millisec']
            price_1 = float(f1.iloc[i]['Last_Price'])

            bid_price1 = float(f1.iloc[i]['Bid_Price1'])
            ask_price1 = float(f1.iloc[i]['Ask_Price1'])
            if len(str(update_time)) == 8:
                try:
                    price_2 = float(f2[f2['Update_Time']==update_time]['Last_Price'])
                    bid_price2 = float(f2[f2['Update_Time']==update_time]['Bid_Price1'].values[0])
                    ask_price2 = float(f2[f2['Update_Time']==update_time]['Ask_Price1'].values[0])
                    last_bid_price_second_main = bid_price2
                    last_ask_price_second_main = ask_price2
                    last_price_second_main = price_2
                except:
                    if last_price_second_main != 0:
                        price_2 = last_price_second_main
                    if last_bid_price_second_main != 0:
                        bid_price2 = last_bid_price_second_main
                        ask_price2 = last_ask_price_second_main
                    else:
                        continue

                # 俩合约最新价价差
                last_price_delta = price_1 - price_2
                price_delta_list.append(last_price_delta)
                price_delta_data_frame_list.append([last_price_delta])

                if len(price_delta_list) <= set_ma:
                    continue

                price_delta_list.pop(0)
                price_delta_data_frame_list.pop(0)

                # price_delta_ma = talib.MA(np.array(price_delta_list), set_ma)[-1]
                price_delta_ma_data_frame = pd.DataFrame(price_delta_data_frame_list, columns=['Last_Price_Delta'])

                mean_value = price_delta_ma_data_frame.mean()[0]
                short_mean_arr = np.array(price_delta_ma_data_frame.values)[-short_ma:]
                short_mean_value = np.mean(short_mean_arr)
                std_value  = price_delta_ma_data_frame.std()[0]

                if flag == 0:
                    if bid_price1 - bid_price2 <= mean_value - set_std * std_value:#and bid_price1 - bid_price2 >= short_mean_value - set_std * std_value:
                        open_price = bid_price1 - bid_price2
                        print u"开仓: " + update_time + ' ' + str(open_price)
                        flag = 1
                        direction = 0
                    elif ask_price1 - ask_price2 >= mean_value + set_std * std_value:#and ask_price1 - ask_price2 <= short_mean_value + set_std * std_value:
                        open_price = ask_price1 - ask_price2
                        print u"开仓: " + update_time + ' ' + str(open_price)
                        flag = 1
                        direction = 1
                    else:
                        direction = -1

                elif flag == 1:
                    if bid_price1 - bid_price2 <= mean_value - set_std * std_value:# and bid_price1 - bid_price2 >= short_mean_value - set_std * std_value and direction == 1:
                        ping_price = bid_price1 - bid_price2
                        print u"平仓: " + update_time + ' ' + str(ping_price)
                        times += 1
                        e_l_tot += open_price - ping_price
                        flag = 0
                    elif ask_price1 - ask_price2 >= mean_value + set_std * std_value:# and ask_price1 - ask_price2 <= short_mean_value + set_std * std_value and direction == 0:
                        ping_price = ask_price1 - ask_price2
                        print u"平仓: " + update_time + ' ' + str(ping_price)
                        times += 1
                        e_l_tot += ping_price - open_price
                        flag = 0


    return e_l_tot, times


if __name__ == '__main__':
    # 日期选择
    date_start = 20170901
    date_end   = 20170901

    # # 合约选择
    # instrument_id_1 = "RU1709"
    # instrument_id_2 = "RU1801"

    # 合约选择
    instrument_id_1 = "ZN1710"
    instrument_id_2 = "ZN1711"

    result_dict = {}

    # 设置的移动平均周期数
    set_ma  = 800
    short_ma = 20

    # # 标准差倍数设置
    # set_std = 1.0

    set_ma_list = range(200, 1020, 40)

    set_std_list = [1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 3.0]
    # set_std_list = [0.5]

    for set_ma in set_ma_list:
        for set_std in set_std_list:
            earn, times = get_data(date_start, date_end, instrument_id_1, instrument_id_2, set_ma, short_ma, set_std)

            result_dict[str(set_ma)+','+str(set_std)] = [earn, times]

    result_list = sorted(result_dict.iteritems(), key=lambda asd: abs(asd[1][0]), reverse=True)

    out_put_file = instrument_id_1 + '_' + instrument_id_2 + '_' + str(date_start) + '_' + str(date_end) + '.txt'
    output = open(out_put_file, 'w')
    title = "最优组合如下: "
    print title
    print >>output, title
    for combine in result_list[0:100]:
        cmd = str(combine[0])  + ' ' + str(combine[1][0]) + ' ' + str(combine[1][1])
        print cmd
        print >>output, cmd
