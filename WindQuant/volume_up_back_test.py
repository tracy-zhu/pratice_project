# -*- coding: utf-8 -*-

from WindPy import *
from datetime import *
import pandas as pd
w.start(show_welcome=False)

list_A = w.wset("SectorConstituent",u"date=20130608;sector=全部A股").Data[1] 

def initialize(context):             #定义初始化函数
    context.capital = 1000000        #回测的初始资金
    context.securities = list_A      #回测标的 这里是全部A股
    context.start_date = "20180101"  #回测开始时间
    context.end_date = "20180719"    #回测结束时间
    context.period = 'd'             # 'd' 代表日, 'm'代表分钟   表示行情数据的频率
    context.pos = 1                  # 这个的1 表示查看 因子“TURN”最大的10%作为建仓股票 
    context.feature = 'TURN'         #这里 输入 感兴趣的因子-大写  本例中为“TURN” 换手率
    context.benchmark = '000300.SH'  #设置回测基准为沪深300
    context.select_num = 10          #选择排名靠前的多少只股票
    context.buy_money = 10000        # 每次买一只股票的钱；


def handle_data(bar_datetime, context, bar_data):
    pass


def my_schedule1(bar_datetime, context, bar_data):             
    "应用于每天选股，将当天成交放大的股票筛选出，并将没有在现在持有的股票买入"
    limit_pre_pct = 20
    limit_bit_pin_ratio = 0.5
    trading_day = bar_datetime.strftime("%Y-%m-%d")
    start_Date = w.tdaysoffset(-5, trading_day, "").Times[0]
    start_date = start_Date.strftime("%Y-%m-%d")
    wss_str = 'tradedate={trading_day};cycle=1;priceadj=1;startdate={start_date};enddate={end_date}'.format(trading_day=trading_day, start_date=start_date, end_date=trading_day)
    his = w.wss(list_A, "sec_name,open,high,low,close,volume,pct_chg,avg_vol_per,pct_chg_per", wss_str)
    # his = w.wss("000001.SZ,600000.SH", "avg_vol_per,avg_amt_per", "startDate=2018-06-15;endDate=2018-07-15")
    data = pd.DataFrame(his.Data,columns=his.Codes,index=his.Fields).T
    data['volume_up_ratio'] = data["VOLUME"] / data["AVG_VOL_PER"]
    data['is_exists'] = (data["HIGH"] - data["LOW"])
    data = data[data['is_exists'] != 0]
    data = data[data['PCT_CHG'] <= 9]
    data['bit_pin_ratio'] = (data["HIGH"] - data["CLOSE"]) / (data["HIGH"] - data["LOW"])
    data['day_pct']  = data["CLOSE"] - data["OPEN"]
    data = data[data['day_pct'] > 0]
    data = data[data['PCT_CHG_PER'] < limit_pre_pct]
    data = data[data['bit_pin_ratio'] < limit_bit_pin_ratio]
    sort_df = data.sort_values(by='volume_up_ratio', ascending=False)
    select_code_list = list(sort_df.index[:context.select_num])
    position_code_list = list(wa.query_position().get_field('code'))
    trade_code_list = list(set(select_code_list + position_code_list))
    wa.change_securities(trade_code_list)
    context.securities = trade_code_list
    for stock_code in select_code_list:
        if stock_code not in position_code_list:
            res = wa.order_value(stock_code, context.buy_money, 'buy', price='close')


def my_schedule2(bar_datetime, context, bar_data):             
    """
    根据绝对止损，绝对止盈，和持有天数，对持仓的股票进行平仓；
    或者根据技术指标也可以；
    持有天数搞不定，用技术指标优化吧
    """
    position_df = wa.query_position()
    if position_df != None:
        for stock_code in position_df['code']:
            revenue = position_df[stock_code]['revenue']
            volume = position_df[stock_code]['volume']
            revenue_ratio = float(revenue) / context.buy_money
            if revenue_ratio < -0.03 or revenue_ratio > 0.06:
                res = wa.order(stock_code, volume, 'sell', price='close')


wa = BackTest(init_func = initialize, handle_data_func=handle_data)   #实例化回测对象
wa.schedule(my_schedule1, "d", 0)         #   m表示在每个月执行一次策略 0表示偏移  表示月初第一个交易日往后0天
wa.schedule(my_schedule2, "d", 1)         #在月初第2个交易进行交易
res = wa.run(show_progress=True)          #调用run()函数开始回测,show_progress可用于指定是否显示回测净值曲线图
nav_df = wa.summary('nav')                  #获取回测结果  回测周期内每一天的组合净值
history_pos = wa.summary('trade')             #可以查看历史持仓记录