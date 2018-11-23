# -*- coding: utf-8 -*-
"""
Created on Mon May 16 09:27:26 2016

@author: Tracy Zhu
"""
import sys
from pandas import Series
import xml.dom.minidom
import math

from datetime import datetime, timedelta

# 导入用户库
sys.path.append("..")
from python_base.Line_Text_To_Best_Marketdata import *
from python_base.Quote_File_Manage import *
from python_base.common_method import *

#  全局变量
# g_tick_quote_file_root_folder = "\\\\192.168.1.203\\quote_server_bak\\Quote_Data\\Tick_Quote"
g_tick_quote_file_root_folder = "Z:\\"
g_tick_columns = ['Instrument_ID', 'Update_Time', 'Update_Millisec', 'Trading_Day', 'Pre_Settlement_Price',
                  'Pre_Close_Price', 'Pre_Open_Interest',
                  'Pre_Delta', 'Open_Price', 'Highest_Price', 'Lowest_Price', 'Close_Price', 'Upper_Limit_Price',
                  'Lower_Limit_Price', 'Settlement_Price',
                  'Curr_Delta', 'Life_High', 'Life_Low', 'Last_Price', 'Last_Match_Volume', 'Turnover',
                  'Total_Match_Volume', 'Open_Interest', 'Interest_Change',
                  'Average_Price', 'Bid_Price1', 'Bid_Volume1', 'Ask_Price1', 'Ask_Volume1', 'Exchange_ID']
trade_phase_file_name = "C:\\Users\\Tracy Zhu\\Desktop\\trade_phase\\20160503-99999999_trade_phase.xml"
g_dom = xml.dom.minidom.parse(trade_phase_file_name)
variety_id_array = ['RU', 'RB', 'NI', 'SR', 'CF', 'TA', 'RM', 'OI', 'CU', 'AL', 'ZN', 'BU', 'AG', 'FG', 'WH', 'MA', 'HC', 'ZC', 'PB', 'SN', 'AU', 'CY']
latency_variety_id_array = ['NI', 'CU', 'AL', 'ZN', 'RU']
trigger_price_range_dict = {'RU': [70, 70, 90], 'RB': [14, 22, 30], 'NI': [220, 300], 'CU': [160, 170, 170, 200, 300], 'AL': [70, 80, 90, 100, 120], 'ZN': [70, 85, 120, 140],
                            'AU': [1.3], 'AG': [18, 40], 'HC': [15, 30], 'BU': [24, 36, 60, 64], 'SR': [13, 20, 40], 'CF': [40, 80],
                            'TA': [18, 50, 80], 'FG': [9, 20, 40], 'WH': [40, 80], 'ZC': [3, 5], 'CY': [80],
                            'RM': [8, 25, 45], 'OI': [18, 28], 'MA': [9, 20], 'PB': [110, 130, 150], 'SF': [40], 'SM':[40], 'SN':[400]}
open_order_volume_dict = {'RU': [8], 'RB': [30], 'NI': [1], 'CU': [4], 'AL': [12], 'ZN': [8], 'AU': [6], 'AG': [18], 'CY':[10],
                          'HC': [12], 'BU': [15], 'SR': [20], 'CF': [6], 'TA': [8], 'MA': [20], 'FG': [10], 'ZC': [9],
                          'RM': [20], 'OI': [12], 'WH': [3], 'PB': [4], 'SF': [4], 'SM':[4], 'SN':[4]}
max_open_order_volume_dict = {'RU': [30], 'RB': [360], 'NI': [30], 'CU': [50], 'AL': [50], 'ZN': [50], 'AU': [45], 'CY':[30],
                              'AG': [200], 'HC': [450], 'BU': [360], 'SR': [50], 'CF': [50], 'TA': [50], 'MA': [50],
                              'RM': [50], 'OI': [30], 'FG':[40], 'WH':[20], 'ZC': [40], 'PB': [155], 'SF': [6], 'SM':[6], 'SN':[90]}
stop_tick_dict = {'RU': [4], 'RB': [5], 'NI': [4], 'CU': [6], 'AL': [8], 'ZN': [4], 'AU': [6], 'AG': [4],
                          'HC': [7], 'BU': [6], 'SR': [6], 'CF': [6], 'TA': [6], 'MA': [7], 'FG': [6], 'ZC': [5],
                          'RM': [6], 'OI': [6], 'WH': [4], 'PB': [5], 'SF': [6], 'SM':[6], 'SN':[60], 'CY' :[6]}
extreme_price_range_dict = {'RU': [300], 'RB': [45], 'NI': [600], 'CU': [500], 'AL': [250], 'ZN': [250],
                            'AU': [3], 'AG': [42], 'HC': [45], 'BU': [100], 'SR': [42], 'CF': [80],
                            'TA': [80], 'FG': [40], 'WH': [90], 'ZC': [6], 'CY':[200],
                            'RM': [50], 'OI': [40], 'MA': [30], 'PB': [200], 'SF': [60], 'SM':[60], 'SN':[800]}
two_variety_list = ['AL', 'ZN', 'CU', 'SR', 'CF', 'TA', 'RM', 'OI', 'MA', 'WH', 'RU', 'AG', 'BU', 'ZC', 'FG', 'RB', 'HC', 'PB', 'NI']
three_variety_list = ['CU', 'SR', 'RM', 'FG', 'TA', 'AL', 'ZN', 'RB', 'PB', 'BU', 'RU']
forth_variety_list = ['CU', 'AL', 'ZN', 'BU']
fifth_variety_list = ['AL', 'CU']
now = datetime.now()
trading_day = now.strftime('%Y%m%d')
#trading_day = '20170927'
month_str = trading_day[-4:-2]
if month_str == '12':
    pre_month_str = '01'
else:
    pre_month_num = int(month_str) + 1
    pre_month_str = str(pre_month_num).zfill(2)

trading_day_list = get_trading_day_list()
close_limit_update_time = "14:58:00"
open_time = '20:59:00'
main_order_volume = 1
main_lost_tick_num = 4
total_volume_limit_ratio = 1.5
open_volume_ma_limit_ratio = 2.5
spam_num = 8
first_level_volume = 70
second_level_volume = 80
third_level_volume = 100
reserved_tick = 5


line1 = "<auction_arbi_config>\n"
line2 = "\t<auction_arbi_list>\n"
line11 = "\t</auction_arbi_list>\n"
line12 = "</auction_arbi_config>\n"


def get_open_volume(main_quote_data):
    optimal_volume = 0
    main_open_quote = main_quote_data[main_quote_data.Update_Time == open_time]
    if len(main_open_quote) > 0:
        optimal_volume = main_open_quote.Total_Match_Volume.values[0]
        optimal_volume = optimal_volume / 2
    return optimal_volume


def get_open_volume_series(instrument_id, trading_day):
    open_volume_list = []
    trading_day_time = datetime.strptime(trading_day, '%Y%m%d')
    pre_trading_day = trading_day_time - timedelta(days=14)
    for trade_day in pd.date_range(pre_trading_day, trading_day_time):
        trading_day_str = trade_day.strftime('%Y%m%d')
        if (trading_day_str + '\n') in trading_day_list:
            main_quote_data = read_data(instrument_id, trading_day_str)
            open_volume = get_open_volume(main_quote_data)
            if open_volume != 0:
                open_volume_list.append(open_volume)
            print (trading_day_str, open_volume)
    open_volume_arr = np.array(open_volume_list)
    mean_volume = open_volume_arr[:-1].mean()
    last_open_volume = open_volume_list[-1]
    return last_open_volume, mean_volume


def get_variety_id(instrument_name):
    variety_id = instrument_name[0]
    if instrument_name[1] >= "A" and instrument_name[1] <= "Z":
        variety_id = variety_id + instrument_name[1]
    return variety_id


folder_path = g_tick_quote_file_root_folder + "\\" + trading_day
if folder_path is None:
    raise Exception("folder_path is None")

instrument_file_list = {}
for dirpath, dirnames, filenames in os.walk(folder_path):
    for name in filenames:
        # print name
        if len(name) < 7 + 4:
            variety_id = get_variety_id(name)
            if variety_id in variety_id_array:
                if instrument_file_list.has_key(variety_id):
                    pass
                else:
                    instrument_file_list[variety_id] = []
                instrument_file_list[variety_id].append(dirpath + '\\' + name)


def get_attribution(variety_id):
    global g_dom
    root = g_dom.documentElement
    itemlist = root.getElementsByTagName('VarietyPhase')
    for item in itemlist:
        if variety_id == item.getAttribute("varietyid").encode("gbk"):
            tick = float(item.getAttribute("tick").encode("gbk"))
            exchtype = float(item.getAttribute("exchtype").encode("gbk"))
            exchange_id = ''
            if exchtype == 3:
                exchange_id = "CZCE"
            elif exchtype == 2:
                exchange_id = "SHFE"
            return tick, exchange_id


def check_close_price_by_variety_id(variety_id, instrument_list):
    global month_str, pre_month_str
    global close_limit_update_time
    sixth_instrument = None
    quote_map = {}
    for one_file_name in instrument_list:
        quote_file = open(one_file_name, "r")
        quote_list = quote_file.readlines()
        quote_file.close()
        instrument_id = one_file_name.split("\\")[-1].split(".")[0]
        close_quote = CBest_Market_Data_Field()
        if len(quote_list) > 3:
            if len(quote_list[-1]) > 2:
                close_quote = Get_CBest_Market_Data_Field_From_Line(quote_list[-2])
            else:
                close_quote = Get_CBest_Market_Data_Field_From_Line(quote_list[-3])
            quote_map[instrument_id] = close_quote

    if len(quote_map) > 2:
        # 寻找主力合约
        best_quote_frame = Series()
        for (instrument_id, close_quote) in quote_map.items():
            if instrument_id[-2:] != month_str:
                best_quote = Series([instrument_id, close_quote.Total_Match_Volume])
                best_quote_frame = best_quote_frame.append(best_quote)
        best_quote_frame = Series(best_quote_frame[1].values, index=best_quote_frame[0].values)
        best_quote_frame.sort()
        main_instrument = best_quote_frame.index[-1]
        sub_instrument = best_quote_frame.index[-2]
        ssub_instrument = best_quote_frame.index[-3]
        forth_instrument = best_quote_frame.index[-4]
        fifth_instrument = best_quote_frame.index[-5]
        if len(best_quote_frame.index) > 5:
            sixth_instrument = best_quote_frame.index[-6]
        first_instrument = main_instrument
        second_instrument = sub_instrument
        trigger_ref_spread_price = (float(quote_map[main_instrument].Bid_Price1) + float(quote_map[main_instrument].Ask_Price1)) / 2 - \
                                   (float(quote_map[second_instrument].Bid_Price1) + float(quote_map[second_instrument].Ask_Price1)) / 2
        tick, exchange_id = get_attribution(variety_id)

        if second_instrument[-2:] == pre_month_str:
            trigger_price_range = trigger_price_range_dict[variety_id][0] + 10 * tick
        else:
            trigger_price_range = trigger_price_range_dict[variety_id][0] 

        extreme_price_range = extreme_price_range_dict[variety_id][0]
        open_order_volume = open_order_volume_dict[variety_id][0]
        max_open_order_volume = max_open_order_volume_dict[variety_id][0]
        stop_tick = stop_tick_dict[variety_id][0] * tick
        line4 = "\t\t\t<main_instrument>" + main_instrument + "</main_instrument>\n"
        line6 = "\t\t\t<sub_instrument>" + second_instrument + "</sub_instrument>\n"
        line7 = "\t\t\t<open_order_volume>" + str(int(open_order_volume)) + "</open_order_volume>\n"
        line71 = "\t\t\t<stop_tick>" + str(float(stop_tick)) + "</stop_tick>\n"
        line8 = "\t\t\t<tigger_ref_spread_price>" + str(trigger_ref_spread_price) + "</tigger_ref_spread_price>\n"
        line9 = "\t\t\t<tigger_price_range>" + str(int(trigger_price_range)) + "</tigger_price_range>\n"
        line91 = "\t\t\t<price_multiple>" + str(float(tick) * 2) + "</price_multiple>\n"
        line92 = "\t\t\t<order_multiple>" + str(int(math.ceil(float(open_order_volume) / 2))) + "</order_multiple>\n"
        line93 = "\t\t\t<max_open_order_volume>" + str(int(max_open_order_volume)) + "</max_open_order_volume>\n"
        line10 = "\t\t</auction_arbi_variety>\n"
        line_add1 = "\t\t\t<open_over_take>" + str(float(tick)) + "</open_over_take>\n"
        line_add2 = "\t\t\t<extreme_price_range>" + str(int(extreme_price_range)) + "</extreme_price_range>\n"
        line_add4 = "\t\t\t<main_order_volume>" + str(int(main_order_volume)) + "</main_order_volume>\n"
        line_add5 = "\t\t\t<main_lost_tick>" + str(float(main_lost_tick_num * tick)) + "</main_lost_tick>\n"
        line_add6 =  "\t\t\t<total_volume_limit_ratio>" + str(float(total_volume_limit_ratio)) + "</total_volume_limit_ratio>\n"
        line_add7 = "\t\t\t<spam_num>" + str(int(spam_num)) + "</spam_num>\n"
        line_add8 = "\t\t\t<first_level_volume>" + str(int(first_level_volume)) + "</first_level_volume>\n"
        line_add9 = "\t\t\t<second_level_volume>" + str(int(second_level_volume)) + "</second_level_volume>\n"
        line_add10 = "\t\t\t<third_level_volume>" + str(int(third_level_volume)) + "</third_level_volume>\n"
        line_add11 = "\t\t\t<reserved_profit>" + str(reserved_tick * float(tick)) + "</reserved_profit>\n"
        if exchange_id == 'SHFE':
            _, mean_volume = get_open_volume_series(main_instrument, trading_day)
            if variety_id not in latency_variety_id_array:
                line3 = "\t\t<auction_arbi_variety  exchange_id=\"" + exchange_id + "\" variety_id=\"" + variety_id + \
                        "\" tick=\"" + str(float(tick)) + "\" trigger_time=\"20:58:59.700\"" + " try_czce_order_time=\"20:58:30.000\">\n"
            else:
                line3 = "\t\t<auction_arbi_variety  exchange_id=\"" + exchange_id + "\" variety_id=\"" + variety_id + \
                        "\" tick=\"" + str(float(tick)) + "\" trigger_time=\"20:58:59.400\"" + " try_czce_order_time=\"20:58:30.000\">\n"
                line93 = "\t\t\t<max_open_order_volume>" + str(int(max_open_order_volume / 2)) + "</max_open_order_volume>\n"
            line_add3 = "\t\t\t<main_average_his_volume>" + str(int(mean_volume * open_volume_ma_limit_ratio)) + "</main_average_his_volume>\n"
            print>> reach_limit_price_result_file, line3, line4, line6, line7, line71, line8, line9, line91, line_add1, line_add2, line92, \
                line93, line_add3, line_add4, line_add5, line_add6, line_add7, line_add8, line_add9, line_add10, line_add11, line10
            reach_limit_price_result_file.flush()
        else:
            line3 = "\t\t<auction_arbi_variety  exchange_id=\"" + exchange_id + "\" variety_id=\"" + variety_id + \
                    "\" tick=\"" + str(float(tick)) + "\" trigger_time=\"20:58:59.450\"" + " try_czce_order_time=\"20:58:30.000\">\n"
            line_add3 = "\t\t\t<main_average_his_volume>" + str(200) + "</main_average_his_volume>\n"
            print>> reach_limit_price_result_file, line3, line4, line6, line7, line71, line8, line9, line91, line_add1, line_add2, line92, \
                line93, line_add3, line_add4, line_add5, line_add6, line_add7, line_add8, line_add9, line_add10, line_add11, line10
            reach_limit_price_result_file.flush()

        if variety_id in two_variety_list:
            second_instrument = ssub_instrument
            trigger_price_range = trigger_price_range_dict[variety_id][1]
            trigger_ref_spread_price = (float(quote_map[main_instrument].Bid_Price1) + float(quote_map[main_instrument].Ask_Price1)) / 2 - \
                                   (float(quote_map[second_instrument].Bid_Price1) + float(quote_map[second_instrument].Ask_Price1)) / 2
            ref_spread_last_price = float(quote_map[main_instrument].Last_Price) - float(quote_map[second_instrument].Last_Price)
            bid_ask_spread = abs(ref_spread_last_price - trigger_ref_spread_price) / tick
            if bid_ask_spread < 15 and quote_map[second_instrument].Update_Time > close_limit_update_time:
                line6 = "\t\t\t<sub_instrument>" + second_instrument + "</sub_instrument>\n"
                line7 = "\t\t\t<open_order_volume>" + str(int(math.ceil(float(open_order_volume) / 2))) + "</open_order_volume>\n"
                line8 = "\t\t\t<tigger_ref_spread_price>" + str(trigger_ref_spread_price) + "</tigger_ref_spread_price>\n"
                line9 = "\t\t\t<tigger_price_range>" + str(int(trigger_price_range)) + "</tigger_price_range>\n"
                line91 = "\t\t\t<price_multiple>" + str(float(tick) * 3) + "</price_multiple>\n"
                line93 = "\t\t\t<max_open_order_volume>" + str(int(max_open_order_volume)) + "</max_open_order_volume>\n"
                line_add1 = "\t\t\t<open_over_take>" + str(float(tick) * 3) + "</open_over_take>\n"
                print>> reach_limit_price_result_file, line3, line4, line6, line7, line71, line8, line9, line91, line_add1, line_add2, line92, \
                    line93, line_add3,  line_add4, line_add5, line_add6, line_add7, line_add8, line_add9, line_add10,line_add11, line10
                reach_limit_price_result_file.flush()

        if variety_id in three_variety_list:
            second_instrument = forth_instrument
            trigger_price_range = trigger_price_range_dict[variety_id][2]
            trigger_ref_spread_price = (float(quote_map[main_instrument].Bid_Price1) + float(quote_map[main_instrument].Ask_Price1)) / 2 - \
                                   (float(quote_map[second_instrument].Bid_Price1) + float(quote_map[second_instrument].Ask_Price1)) / 2
            ref_spread_last_price = float(quote_map[main_instrument].Last_Price) - float(quote_map[second_instrument].Last_Price)
            bid_ask_spread = abs(ref_spread_last_price - trigger_ref_spread_price) / tick
            if bid_ask_spread < 15 and quote_map[second_instrument].Update_Time > close_limit_update_time:
                line6 = "\t\t\t<sub_instrument>" + second_instrument + "</sub_instrument>\n"
                line7 = "\t\t\t<open_order_volume>" + str(int(math.ceil(float(open_order_volume) / 3))) + "</open_order_volume>\n"
                line8 = "\t\t\t<tigger_ref_spread_price>" + str(trigger_ref_spread_price) + "</tigger_ref_spread_price>\n"
                line9 = "\t\t\t<tigger_price_range>" + str(int(trigger_price_range)) + "</tigger_price_range>\n"
                line91 = "\t\t\t<price_multiple>" + str(float(tick) * 5) + "</price_multiple>\n"
                line93 = "\t\t\t<max_open_order_volume>" + str(int(max_open_order_volume)) + "</max_open_order_volume>\n"
                line_add1 = "\t\t\t<open_over_take>" + str(float(tick) * 5) + "</open_over_take>\n"
                print>> reach_limit_price_result_file, line3, line4, line6, line7, line71, line8, line9, line91, line_add1, line_add2, line92, \
                    line93, line_add3, line_add4, line_add5, line_add6, line_add7, line_add8, line_add9, line_add10,line_add11, line10
                reach_limit_price_result_file.flush()

        if variety_id in forth_variety_list:
            second_instrument = fifth_instrument
            trigger_price_range = trigger_price_range_dict[variety_id][3]
            trigger_ref_spread_price = (float(quote_map[main_instrument].Bid_Price1) + float(quote_map[main_instrument].Ask_Price1)) / 2 - \
                                   (float(quote_map[second_instrument].Bid_Price1) + float(quote_map[second_instrument].Ask_Price1)) / 2
            ref_spread_last_price = float(quote_map[main_instrument].Last_Price) - float(quote_map[second_instrument].Last_Price)
            bid_ask_spread = abs(ref_spread_last_price - trigger_ref_spread_price) / tick
            if bid_ask_spread < 15 and quote_map[second_instrument].Update_Time > close_limit_update_time:
                line6 = "\t\t\t<sub_instrument>" + second_instrument + "</sub_instrument>\n"
                line7 = "\t\t\t<open_order_volume>" + str(int(math.ceil(float(open_order_volume) / 5))) + "</open_order_volume>\n"
                line8 = "\t\t\t<tigger_ref_spread_price>" + str(trigger_ref_spread_price) + "</tigger_ref_spread_price>\n"
                line9 = "\t\t\t<tigger_price_range>" + str(int(trigger_price_range)) + "</tigger_price_range>\n"
                line91 = "\t\t\t<price_multiple>" + str(float(tick) * 8) + "</price_multiple>\n"
                line93 = "\t\t\t<max_open_order_volume>" + str(int(max_open_order_volume)) + "</max_open_order_volume>\n"
                line_add1 = "\t\t\t<open_over_take>" + str(float(tick) * 5) + "</open_over_take>\n"
                print>> reach_limit_price_result_file, line3, line4, line6, line7, line71, line8, line9, line91, line_add1, line_add2, line92, \
                    line93, line_add3, line_add4, line_add5, line_add6, line_add7, line_add8, line_add9, line_add10,line_add11, line10
                reach_limit_price_result_file.flush()

        if variety_id in fifth_variety_list:
            ref_spread_last_price = float(quote_map[main_instrument].Last_Price) - float(quote_map[second_instrument].Last_Price)
            bid_ask_spread = abs(ref_spread_last_price - trigger_ref_spread_price) / tick
            if bid_ask_spread < 15 and quote_map[second_instrument].Update_Time > close_limit_update_time:
                second_instrument = sixth_instrument
                trigger_price_range = trigger_price_range_dict[variety_id][4]
                trigger_ref_spread_price = (float(quote_map[main_instrument].Bid_Price1) + float(quote_map[main_instrument].Ask_Price1)) / 2 - \
                                       (float(quote_map[second_instrument].Bid_Price1) + float(quote_map[second_instrument].Ask_Price1)) / 2
                line6 = "\t\t\t<sub_instrument>" + second_instrument + "</sub_instrument>\n"
                line7 = "\t\t\t<open_order_volume>" + str(int(math.ceil(float(open_order_volume) / 5))) + "</open_order_volume>\n"
                line8 = "\t\t\t<tigger_ref_spread_price>" + str(trigger_ref_spread_price) + "</tigger_ref_spread_price>\n"
                line9 = "\t\t\t<tigger_price_range>" + str(int(trigger_price_range)) + "</tigger_price_range>\n"
                line91 = "\t\t\t<price_multiple>" + str(float(tick) * 10) + "</price_multiple>\n"
                line93 = "\t\t\t<max_open_order_volume>" + str(int(max_open_order_volume)) + "</max_open_order_volume>\n"
                line_add1 = "\t\t\t<open_over_take>" + str(float(tick) * 7) + "</open_over_take>\n"
                print>> reach_limit_price_result_file, line3, line4, line6, line7, line71, line8, line9, line91, line_add1, line_add2, line92, \
                    line93, line_add3, line_add4, line_add5, line_add6, line_add7, line_add8, line_add9, line_add10,line_add11, line10
                reach_limit_price_result_file.flush()

reach_limit_price_result_file_folder = "D:\\strategy\\open_price_strategy\\strategy_xml_bak\\" + trading_day + '\\'
isExists = os.path.exists(reach_limit_price_result_file_folder)
if not isExists:
    os.makedirs(reach_limit_price_result_file_folder)
reach_limit_price_result_file_name = reach_limit_price_result_file_folder + 'auction_arbi_config.xml'
reach_limit_price_result_file = open(reach_limit_price_result_file_name, "w")

print>> reach_limit_price_result_file, line1, line2
for (variety_id, instrument_list) in instrument_file_list.items():
    check_close_price_by_variety_id(variety_id, instrument_list)
print>> reach_limit_price_result_file, line11, line12
reach_limit_price_result_file.close()
