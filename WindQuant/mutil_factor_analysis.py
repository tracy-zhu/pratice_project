# -*- coding: utf-8 -*-

from WindPy import *
from datetime import *
import pandas as pd
from WindAlgo import * #引入回测框架
w.start(show_welcome=False)

list_stock =  w.wset("sectorconstituent", "date=2017-08-10;sectorId=a001010100000000").Data[1]     #全部A股 作为初始股票池

def initialize(context):             #定义初始化函数
    context.capital = 1000000        #回测的初始资金
    context.securities = list_stock      #回测标的 这里是全部A股
    context.start_date = "20150101"  #回测开始时间
    context.end_date = "20161231"    #回测结束时间
    context.period = 'd'             # 'd' 代表日, 'm'代表分钟   表示行情数据的频率
    context.benchmark = '000300.SH'  #设置回测基准为沪深300

def handle_data(bar_datetime, context, bar_data):
    pass
    
def my_schedule1(bar_datetime, context, bar_data): # 注意：schedule函数里不能加入新的参数

    bar_datetime_str = bar_datetime.strftime('%Y-%m-%d')                #设置时间
    data = w.wss(list_stock,"tot_assets,tot_cur_assets,tot_cur_liab,surplus_rsrv,undistributed_profit,qfa_fin_exp_is,qfa_tot_profit,qfa_tot_oper_rev,tot_liab,free_float_shares,total_shares,close,tot_equity","unit=1;rptDate=LYR;rptType=1;tradeDate="+bar_datetime_str+";priceAdj=U;cycle=D")
    #LYR表示财报数据报告期返回去年年报 下载每个月初的截面数据  
    data = pd.DataFrame(data.Data,columns=data.Codes,index=data.Fields).T  #改变格式为数据框            
    data = data.dropna()                      #删除有缺失的记录
    
    data['x1'] = (data['TOT_CUR_ASSETS']-data['TOT_CUR_LIAB'])/data['TOT_ASSETS']
    data['x2'] = (data['UNDISTRIBUTED_PROFIT']+data['SURPLUS_RSRV'])/data['TOT_ASSETS']
    data['x3'] = (data['QFA_TOT_PROFIT']+data['QFA_FIN_EXP_IS'])/data['TOT_ASSETS']
    data['x4'] = (data['CLOSE']*data['FREE_FLOAT_SHARES']+data['TOT_EQUITY']/data['TOTAL_SHARES']*(data['TOTAL_SHARES']-data['FREE_FLOAT_SHARES']))/data['TOT_LIAB']
    data['x5'] = data['QFA_TOT_OPER_REV']/data['TOT_ASSETS']
    data['z'] = 1.2*data['x1']+1.4*data['x2']+3.3*data['x3']+0.6*data['x4']+1.0*data['x5']    #沿用前人所用的权重 

    data = data.sort_values('z')             #按z得分排序
    code_list = list(data[-round(len(data)/10):].index)    #选择z得分最大的10%
    wa.change_securities(code_list)
    context.securities = code_list    #改变证券池 

    list_sell = wa.query_position().get_field('code')     #此处可改进 有些下个月打算买的股票可以不用卖出只需要调仓即可 可节省一些手续费
    for code in list_sell:
        volumn = wa.query_position()[code]['volume']    #找到每个code 的 持仓量 
        res = wa.order(code,volumn,'sell',price='close', volume_check=False)  # 卖出上一个月初 买入的所有的股票
    ## '卖出上个月所有仓位'  为本月的建仓做准备  
    
def my_schedule2(bar_datetime, context,bar_data):
    
    buy_code_list=list(set(context.securities)-(set(context.securities)-set(list(bar_data.get_field('code')))))  # 在单因子选股的结果中 剔除 没有行情的股票
    for code in buy_code_list:
        res = wa.order_percent(code,1/len(buy_code_list),'buy',price='close', volume_check=False)  
    #对最终选择出来的股票建仓 每个股票仓位相同   '本月建仓完毕'
        
wa = BackTest(init_func = initialize, handle_data_func=handle_data)   #实例化回测对象
wa.schedule(my_schedule1, "m", 0)         #   m表示在每个月执行一次策略 0表示偏移  表示月初第一个交易日往后0天
wa.schedule(my_schedule2, "m", 1)         #在月初第2个交易进行交易
res = wa.run(show_progress=True)          #调用run()函数开始回测,show_progress可用于指定是否显示回测净值曲线图
nav_df = wa.summary('nav')                  #获取回测结果  回测周期内每一天的组合净值
history_pos = wa.summary('trade')             #可以查看历史持仓记录


from WindPy import *
from datetime import *
import pandas as pd
w.start(show_welcome=False)

list_A = w.wset("SectorConstituent",u"date=20130608;sector=全部A股").Data[1]      # 全部A股  作为初始股票池

from WindAlgo import * #引入回测框架

def initialize(context):             #定义初始化函数
    context.capital = 1000000        #回测的初始资金
    context.securities = list_A      #回测标的 这里是全部A股
    context.start_date = "20150101"  #回测开始时间
    context.end_date = "20170401"    #回测结束时间
    context.period = 'd'             # 'd' 代表日, 'm'代表分钟   表示行情数据的频率
    context.pos = 1                  # 这个的1 表示查看 因子“TURN”最大的10%作为建仓股票 
    context.feature = 'TURN'         #这里 输入 感兴趣的因子-大写  本例中为“TURN” 换手率
    context.benchmark = '000300.SH'  #设置回测基准为沪深300


def handle_data(bar_datetime, context, bar_data):
    pass
    

def my_schedule1(bar_datetime, context, bar_data):             # 注意：schedule函数里不能加入新的参数

    field = context.feature                                    #选择要下载的特征
    bar_datetime_str = bar_datetime.strftime('%Y-%m-%d')           #设置时间
    data = w.wss(list_A,field,"tradeDate="+bar_datetime_str+";priceAdj=U;cycle=M;unit=1;gRateType=1;rptDate=LYR;rptType=1") #LYR表示财报数据报告期返回去年年报 下载每个月初的截面数据  
    data= pd.DataFrame(data.Data,columns=data.Codes,index=data.Fields).T  #改变格式为数据框         
    data = data.fillna(0)                                      #缺失设置为0
    data = data[data[context.feature]!=0]                      #因子为缺失的记录删除

    data = data.sort_values(context.feature)    #截面按因子排序 注意是 由小到大的排序
    code_list = list(data[-(round(len(data)/10)*context.pos):].index)  #选择最后10%的股票 即因子最大的10%的股票
    wa.change_securities(code_list)
    context.securities = code_list    #改变证券池 
    
    list_sell = list(wa.query_position().get_field('code'))     #此处可改进 有些下个月打算买的股票可以不用卖出只需要调仓即可 可节省一些手续费
    for code in list_sell:
        volumn = wa.query_position()[code]['volume']    #找到每个code 的 持仓量 
        res = wa.order(code,volumn,'sell',price='close', volume_check=False)  # 卖出上一个月初 买入的所有的股票
    ## '卖出上个月所有仓位'  为本月的建仓做准备  


def my_schedule2(bar_datetime, context,bar_data):
    
    buy_code_list=list(set(context.securities)-(set(context.securities)-set(list(bar_data.get_field('code')))))  # 在单因子选股的结果中 剔除 没有行情的股票
    for code in buy_code_list:
        res = wa.order_percent(code,1/len(buy_code_list),'buy',price='close', volume_check=False)  
        #对最终选择出来的股票建仓 每个股票仓位相同   '本月建仓完毕'


wa = BackTest(init_func = initialize, handle_data_func=handle_data)   #实例化回测对象
wa.schedule(my_schedule1, "m", 0)         #   m表示在每个月执行一次策略 0表示偏移  表示月初第一个交易日往后0天
wa.schedule(my_schedule2, "m", 1)         #在月初第2个交易进行交易
res = wa.run(show_progress=True)          #调用run()函数开始回测,show_progress可用于指定是否显示回测净值曲线图
nav_df = wa.summary('nav')                  #获取回测结果  回测周期内每一天的组合净值