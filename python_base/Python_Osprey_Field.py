## -*- coding: gb2312 -*

from python_base.Python_Data_Type import *

#响应信息
class CRsp_Info_Field:
    def __init__(self):
		#错误代码
		self.Error_ID = CError_ID_Type() 
		#错误信息
		self.Error_Msg = CError_Msg_Type() 

#客户登录
class CCustomer_Login_Field:
    def __init__(self):
		#客户在系统中的编号，编号唯一且遵循交易所制定的编码规则
		self.Customer_ID = CCustomer_ID_Type() 
		#密码
		self.Password = CPassword_Type() 
		#客户端的报单ID，系统只是记录并返回，不处理该字段
		self.Customer_Order_Local_ID = COrder_Local_ID_Type() 

#客户登录退出
class CCustomer_Logout_Field:
    def __init__(self):
		#客户在系统中的编号，编号唯一且遵循交易所制定的编码规则
		self.Customer_ID = CCustomer_ID_Type() 
		#密码
		self.Password = CPassword_Type() 

#系统用户登录
class CSystem_User_Login_Field:
    def __init__(self):
		#用户代码
		self.System_User_ID = CSystem_User_ID_Type() 
		#密码
		self.Password = CPassword_Type() 

#系统用户登录退出
class CSystem_User_Logout_Field:
    def __init__(self):
		#用户代码
		self.System_User_ID = CSystem_User_ID_Type() 
		#密码
		self.Password = CPassword_Type() 

#交易所交易日
class CExchange_Trading_Day_Field:
    def __init__(self):
		#交易发生的日期
		self.Trading_Day = CDate_Type() 
		#一个交易所的编号
		self.Exchange_ID = CExchange_ID_Type() 

#交易所
class CExchange_Field:
    def __init__(self):
		#一个交易所的编号
		self.Exchange_ID = CExchange_ID_Type() 
		#交易所名称
		self.Exchange_Name = CExchange_Name_Type() 

#系统用户
class CSystem_User_Field:
    def __init__(self):
		#
		self.System_User_ID = CSystem_User_ID_Type() 
		#
		self.System_User_Name = CSystem_User_Name_Type() 
		#0：系统管理员 1：超级用户 2: 业务管理员
		self.System_User_Type = CSystem_User_Type_Type() 
		#密码
		self.Password = CPassword_Type() 
		#
		self.Is_Active = CBool_Type() 

#客户
class CCustomer_Field:
    def __init__(self):
		#客户在系统中的编号，编号唯一且遵循交易所制定的编码规则
		self.Customer_ID = CCustomer_ID_Type() 
		#客户名称
		self.Customer_Name = CParty_Name_Type() 
		#自然人，法人
		self.Customer_Type = CCustomer_Type_Type() 
		#密码
		self.Password = CPassword_Type() 
		#客户端的报单ID，系统只是记录并返回，不处理该字段
		self.Customer_Order_Local_ID = COrder_Local_ID_Type() 
		#正常，只可平仓，禁止交易
		self.Customer_Status = CCustomer_Status_Type() 

#品种
class CVariety_Field:
    def __init__(self):
		#一个交易所的编号
		self.Exchange_ID = CExchange_ID_Type() 
		#商品名称
		self.Variety_Name = CVariety_Name_Type() 
		#商品代码
		self.Variety_ID = CVariety_ID_Type() 
		#品种的每手交易的规定数量，针对基础的商品
		self.Volume_Multiple = CVolume_Multiple_Type() 
		#价格小数位
		self.Price_Decimal = CPrice_Decimal_Type() 
		#合约的单位价格涨跌变化的最小值
		self.Price_Tick = CPrice_Type() 
		#市场价报单的最大下单量
		self.Max_Market_Order_Volume = CVolume_Type() 
		#市场价报单的最小下单量
		self.Min_Market_Order_Volume = CVolume_Type() 
		#限价报单的最大下单量
		self.Max_Limit_Order_Volume = CVolume_Type() 
		#限价报单的最小下单量
		self.Min_Limit_Order_Volume = CVolume_Type() 
		#最大持仓量
		self.Max_Limit_Position_Volume = CVolume_Type() 
		#保证金率
		self.Margin_Rate = CRatio_Type() 
		#手续费率
		self.Fee_Rate = CRatio_Type() 
		#平今手续费
		self.Offset_Today_Rate = CRatio_Type() 
		#月份标志
		self.Month_Flag = CMonth_Flag_Type() 

#合约信息
class CInstrument_Field:
    def __init__(self):
		#品种在系统中的编号
		self.Variety_ID = CVariety_ID_Type() 
		#表明合约的持仓类型
		self.Position_Type = CPosition_Type_Type() 
		#品种的每手交易的规定数量，针对基础的商品
		self.Volume_Multiple = CVolume_Multiple_Type() 
		#一个交易所的编号
		self.Exchange_ID = CExchange_ID_Type() 
		#合约在系统中的编号
		self.Instrument_ID = CInstrument_ID_Type() 
		#合约的名称
		self.Instrument_Name = CInstrument_Name_Type() 
		#该合约规定进行实物交割的年份
		self.Delivery_Year = CYear_Type() 
		#该合约规定进行实物交割的月份
		self.Delivery_Month = CMonth_Type() 
		#市场价报单的最大下单量
		self.Max_Market_Order_Volume = CVolume_Type() 
		#市场价报单的最小下单量
		self.Min_Market_Order_Volume = CVolume_Type() 
		#限价报单的最大下单量
		self.Max_Limit_Order_Volume = CVolume_Type() 
		#限价报单的最小下单量
		self.Min_Limit_Order_Volume = CVolume_Type() 
		#最大持仓量
		self.Max_Limit_Position_Volume = CVolume_Type() 
		#合约的单位价格涨跌变化的最小值
		self.Price_Tick = CPrice_Type() 
		#保证金率
		self.Margin_Rate = CRatio_Type() 
		#手续费率
		self.Fee_Rate = CRatio_Type() 
		#平今手续费
		self.Offset_Today_Rate = CRatio_Type() 

#当前时间
class CCurrent_Time_Field:
    def __init__(self):
		#当前日期
		self.Curr_Date = CDate_Type() 
		#目前的精确到秒的时间
		self.Curr_Time = CTime_Type() 
		#当前时间（毫秒）
		self.Curr_Millisec = CMillisec_Type() 

#输入报单
class CInput_Order_Field:
    def __init__(self):
		#一个交易所的编号
		self.Exchange_ID = CExchange_ID_Type() 
		#报单编号
		self.Order_Sys_ID = COrder_Sys_ID_Type() 
		#每一位会员在系统中的编码，编号唯一且遵循交易所制定的编码规则
		self.Participant_ID = CParticipant_ID_Type() 
		#交易员在系统中的编号，编号唯一且遵循交易所制定的编码规则
		self.Seat_ID = CSeat_ID_Type() 
		#客户在系统中的编号
		self.Customer_ID = CCustomer_ID_Type() 
		#客户在各个交易所系统中的编号，编号唯一且遵循交易所制定的编码规则
		self.Customer_Trade_Code = CCustomer_Trade_Code_Type() 
		#合约在系统中的编号
		self.Instrument_ID = CInstrument_ID_Type() 
		#限价单或市价单
		self.Order_Price_Type = COrder_Price_Type_Type() 
		#1．买2．卖
		self.Direction = CDirection_Type() 
		#开平方向
		self.Offset_Flag = COffset_Flag_Type() 
		#套保标志
		self.Hedge_Flag = CHedge_Flag_Type() 
		#限价单价格
		self.Limit_Price = CPrice_Type() 
		#报单数量
		self.Volume_Total_Original = CVolume_Type() 
		#IOC、GFS、GFD、GTD、GTC、GFA
		self.Time_Condition = CTime_Condition_Type() 
		#报单指定的之前报单有效的日期
		self.GTD_Date = CDate_Type() 
		#AV、MV、CV
		self.Volume_Condition = CVolume_Condition_Type() 
		#当成交量类型为MV时有效
		self.Min_Volume = CVolume_Type() 
		#1．立即2．止损
		self.Contingent_Condition = CContingent_Condition_Type() 
		#期货合约发生亏损时，为了防止亏损进一步扩大，交易者预先设定的触发限价平仓指令的价位。
		self.Stop_Price = CPrice_Type() 
		#强平原因
		self.Force_Close_Reason = CForce_Close_Reason_Type() 
		#本地报单顺序号
		self.Order_Local_ID = COrder_Local_ID_Type() 
		#自动挂起标志
		self.Is_Auto_Suspend = CBool_Type() 
		#本地指令号,可能对应了多个订单
		self.Order_Local_Instruction_ID = COrder_Local_Instruction_ID_Type() 
		#本地指令类型,定义了指令的执行方式
		self.Order_Local_Instruction_Type = COrder_Local_Instruction_Type_Type() 
		#客户端的报单ID，系统只是记录并返回，不处理该字段
		self.System_User_Order_Local_ID = COrder_Local_ID_Type() 
		#Market收到报文的时间
		self.Receive_Time = CTime_Type() 
		#客户端登录时使用的系统用户名称，也可以是客户号
		self.System_User_ID = CSystem_User_ID_Type() 
		#报盘机的会话ID
		self.Offer_SessionID = COffer_SessionID_Type() 
		#IP地址
		self.IP_Address = CIP_Address_Type() 

#报单操作
class COrder_Action_Field:
    def __init__(self):
		#一个交易所的编号
		self.Exchange_ID = CExchange_ID_Type() 
		#合约在系统中的编号
		self.Instrument_ID = CInstrument_ID_Type() 
		#报单编号
		self.Order_Sys_ID = COrder_Sys_ID_Type() 
		#本地报单编号
		self.Order_Local_ID = COrder_Local_ID_Type() 
		#操作本地编号
		self.Action_Local_ID = COrder_Local_ID_Type() 
		#操作标志
		self.Action_Flag = CAction_Flag_Type() 
		#客户在系统中的编号
		self.Customer_ID = CCustomer_ID_Type() 
		#客户在系统中的编号，编号唯一且遵循交易所制定的编码规则
		self.Customer_Trade_Code = CCustomer_Trade_Code_Type() 
		#交易员在系统中的编号，编号唯一且遵循交易所制定的编码规则
		self.Seat_ID = CSeat_ID_Type() 
		#限价单价格
		self.Limit_Price = CPrice_Type() 
		#报单数量变化
		self.Volume_Change = CVolume_Type() 
		#本地指令号,可能对应了多个订单
		self.Order_Local_Instruction_ID = COrder_Local_Instruction_ID_Type() 
		#本地指令类型,定义了指令的执行方式
		self.Order_Local_Instruction_Type = COrder_Local_Instruction_Type_Type() 
		#客户端的报单ID，系统只是记录并返回，不处理该字段
		self.System_User_Order_Local_ID = COrder_Local_ID_Type() 
		#客户端登录时使用的系统用户名称，也可以是客户号
		self.System_User_ID = CSystem_User_ID_Type() 
		#报盘机的会话ID
		self.Offer_SessionID = COffer_SessionID_Type() 

#成交
class CTrade_Field:
    def __init__(self):
		#一个交易所的编号
		self.Exchange_ID = CExchange_ID_Type() 
		#交易员在系统中的编号，编号唯一且遵循交易所制定的编码规则
		self.Seat_ID = CSeat_ID_Type() 
		#客户在系统中的编号，编号唯一且遵循交易所制定的编码规则
		self.Customer_Trade_Code = CCustomer_Trade_Code_Type() 
		#客户在系统中的编号
		self.Customer_ID = CCustomer_ID_Type() 
		#成交编号
		self.Trade_ID = CTrade_ID_Type() 
		#合约在系统中的编号
		self.Instrument_ID = CInstrument_ID_Type() 
		#1.买2.卖
		self.Direction = CDirection_Type() 
		#1．开仓2．平今3．平昨4．强平
		self.Offset_Flag = COffset_Flag_Type() 
		#1.投机3.套保
		self.Hedge_Flag = CHedge_Flag_Type() 
		#报单编号
		self.Order_Sys_ID = COrder_Sys_ID_Type() 
		#本成交所使用的资金帐户
		self.Account_ID = CAccount_ID_Type() 
		#成交价格
		self.Price = CPrice_Type() 
		#成交数量
		self.Volume = CVolume_Type() 
		#成交时间
		self.Trade_Time = CTime_Type() 
		#成交类型
		self.Trade_Type = CTrade_Type_Type() 
		#成交价来源
		self.Price_Source = CPrice_Source_Type() 
		#本地报单顺序号
		self.Order_Local_ID = COrder_Local_ID_Type() 

#报单
class COrder_Field:
    def __init__(self):
		#一个交易所的编号
		self.Exchange_ID = CExchange_ID_Type() 
		#报单编号
		self.Order_Sys_ID = COrder_Sys_ID_Type() 
		#每一位会员在系统中的编码，编号唯一且遵循交易所制定的编码规则
		self.Participant_ID = CParticipant_ID_Type() 
		#交易员在系统中的编号，编号唯一且遵循交易所制定的编码规则
		self.Seat_ID = CSeat_ID_Type() 
		#客户在系统中的编号
		self.Customer_ID = CCustomer_ID_Type() 
		#客户在各个交易所系统中的编号，编号唯一且遵循交易所制定的编码规则
		self.Customer_Trade_Code = CCustomer_Trade_Code_Type() 
		#合约在系统中的编号
		self.Instrument_ID = CInstrument_ID_Type() 
		#限价单或市价单
		self.Order_Price_Type = COrder_Price_Type_Type() 
		#1．买2．卖
		self.Direction = CDirection_Type() 
		#开平方向
		self.Offset_Flag = COffset_Flag_Type() 
		#套保标志
		self.Hedge_Flag = CHedge_Flag_Type() 
		#限价单价格
		self.Limit_Price = CPrice_Type() 
		#报单数量
		self.Volume_Total_Original = CVolume_Type() 
		#IOC、GFS、GFD、GTD、GTC、GFA
		self.Time_Condition = CTime_Condition_Type() 
		#报单指定的之前报单有效的日期
		self.GTD_Date = CDate_Type() 
		#AV、MV、CV
		self.Volume_Condition = CVolume_Condition_Type() 
		#当成交量类型为MV时有效
		self.Min_Volume = CVolume_Type() 
		#1．立即2．止损
		self.Contingent_Condition = CContingent_Condition_Type() 
		#期货合约发生亏损时，为了防止亏损进一步扩大，交易者预先设定的触发限价平仓指令的价位。
		self.Stop_Price = CPrice_Type() 
		#强平原因
		self.Force_Close_Reason = CForce_Close_Reason_Type() 
		#本地报单顺序号
		self.Order_Local_ID = COrder_Local_ID_Type() 
		#自动挂起标志
		self.Is_Auto_Suspend = CBool_Type() 
		#本地指令号,可能对应了多个订单
		self.Order_Local_Instruction_ID = COrder_Local_Instruction_ID_Type() 
		#本地指令类型,定义了指令的执行方式
		self.Order_Local_Instruction_Type = COrder_Local_Instruction_Type_Type() 
		#客户端的报单ID，系统只是记录并返回，不处理该字段
		self.System_User_Order_Local_ID = COrder_Local_ID_Type() 
		#Market收到报文的时间
		self.Receive_Time = CTime_Type() 
		#客户端登录时使用的系统用户名称，也可以是客户号
		self.System_User_ID = CSystem_User_ID_Type() 
		#报盘机的会话ID
		self.Offer_SessionID = COffer_SessionID_Type() 
		#IP地址
		self.IP_Address = CIP_Address_Type() 
		#报单来源
		self.Order_Source = COrder_Source_Type() 
		#0．全部成交1．部分成交还在队列中2．部分成交不在队列中3．未成交还在队列中4．未成交不在队列中5．撤单
		self.Order_Status = COrder_Status_Type() 
		#报单完成数量
		self.Volume_Traded = CVolume_Type() 
		#报单未完成数量
		self.Volume_Total = CVolume_Type() 
		#报单日期
		self.Insert_Date = CDate_Type() 
		#插入时间
		self.Insert_Time = CTime_Type() 
		#激活时间
		self.Active_Time = CTime_Type() 
		#挂起时间
		self.Suspend_Time = CTime_Type() 
		#最后修改时间
		self.Update_Time = CTime_Type() 
		#撤销时间
		self.Cancel_Time = CTime_Type() 
		#错误信息
		self.Error_Msg = CError_Msg_Type() 
		#冻结手续费
		self.Frzn_Commi = CMoney_Type() 
		#冻结保证金
		self.Frzn_Margin = CMoney_Type() 
		#商品代码
		self.Variety_ID = CVariety_ID_Type() 
		#该合约规定进行实物交割的月份
		self.Delivery_Month = CMonth_Type() 

#客户资金帐户入金
class CAccount_Deposit_Field:
    def __init__(self):
		#资金账号
		self.Account_ID = CAccount_ID_Type() 
		#入金金额
		self.Deposit = CMoney_Type() 

#最优行情
class CBest_Market_Data_Field:
    def __init__(self):
		#合约代码
		self.Instrument_ID = CInstrument_ID_Type() 
		#最后修改时间
		self.Update_Time = CTime_Type() 
		#最后修改毫秒
		self.Update_Millisec = CMillisec_Type() 
		#交易日
		self.Trading_Day = CDate_Type() 
		#昨结算
		self.Pre_Settlement_Price = CPrice_Type() 
		#昨收盘
		self.Pre_Close_Price = CPrice_Type() 
		#昨持仓量
		self.Pre_Open_Interest = CLarge_Volume_Type() 
		#昨虚实度
		self.Pre_Delta = CRatio_Type() 
		#今开盘
		self.Open_Price = CPrice_Type() 
		#最高价
		self.Highest_Price = CPrice_Type() 
		#最低价
		self.Lowest_Price = CPrice_Type() 
		#今收盘
		self.Close_Price = CPrice_Type() 
		#涨停板价
		self.Upper_Limit_Price = CPrice_Type() 
		#跌停板价
		self.Lower_Limit_Price = CPrice_Type() 
		#今结算
		self.Settlement_Price = CPrice_Type() 
		#今虚实度
		self.Curr_Delta = CRatio_Type() 
		#历史最高价
		self.Life_Hight = CPrice_Type() 
		#历史最低价
		self.Life_Low = CPrice_Type() 
		#最新价
		self.Last_Price = CPrice_Type() 
		#最新成交量
		self.Last_Match_Volume = CVolume_Type() 
		#成交金额
		self.Turnover = CMoney_Type() 
		#成交量
		self.Total_Match_Volume = CVolume_Type() 
		#持仓量
		self.Open_Interest = CLarge_Volume_Type() 
		#持仓量变化
		self.Interest_Change = CVolume_Type() 
		#当日均价
		self.Average_Price = CPrice_Type() 
		#申买价一
		self.Bid_Price1 = CPrice_Type() 
		#申买量一
		self.Bid_Volume1 = CVolume_Type() 
		#申卖价一
		self.Ask_Price1 = CPrice_Type() 
		#申卖量一
		self.Ask_Volume1 = CVolume_Type() 
		#一个交易所的编号
		self.Exchange_ID = CExchange_ID_Type() 

#客户持仓应答
class CCustomer_Position_Field:
    def __init__(self):
		#合约在系统中的编号
		self.Instrument_ID = CInstrument_ID_Type() 
		#客户在系统中的编号，编号唯一且遵循交易所制定的编码规则
		self.Customer_ID = CCustomer_ID_Type() 
		#客户在系统中的编号，编号唯一且遵循交易所制定的编码规则
		self.Customer_Trade_Code = CCustomer_Trade_Code_Type() 
		#1．买2．卖
		self.Direction = CDirection_Type() 
		#持仓的当前数量
		self.Position = CVolume_Type() 
		#持仓保证金
		self.Margin = CMoney_Type() 
		#持仓均价
		self.Hold_Average_Price = CPrice_Type() 
		#开仓均价
		self.Open_Average_Price = CPrice_Type() 
		#今日持仓的当前数量
		self.Today_Position = CVolume_Type() 
		#总冻结
		self.Total_Frozen = CVolume_Type() 
		#今日冻结
		self.Today_Frozen = CVolume_Type() 

#交易账户资金信息
class CReal_Account_Field:
    def __init__(self):
		#内部资金帐号的标识
		self.Account_ID = CAccount_ID_Type() 
		#客户在系统中的编号，编号唯一且遵循交易所制定的编码规则
		self.Customer_ID = CCustomer_ID_Type() 
		#上日结存
		self.Last_Remain = CMoney_Type() 
		#出入金
		self.Money_In_Out = CMoney_Type() 
		#等于Total－（Curr_Margin－Available_Collateral）
		self.Available = CMoney_Type() 
		#Available+浮动盈亏
		self.Dyn_Rights = CMoney_Type() 
		#等于Close_Profit + Position_Profit
		self.Profit = CMoney_Type() 
		#平仓造成的盈亏金额
		self.Close_Profit = CMoney_Type() 
		#持仓造成的盈亏金额
		self.Position_Profit = CMoney_Type() 
		#期货持仓占用的保证金
		self.Margin = CMoney_Type() 
		#冻结保证金资金
		self.Forzen_Margin = CMoney_Type() 
		#买冻结保证金
		self.Buy_Margin_Frozen = CMoney_Type() 
		#买冻结保证金
		self.Sell_Margin_Frozen = CMoney_Type() 
		#当日的所有手续费支出
		self.Fee = CMoney_Type() 
		#冻结手续费
		self.Frozen_Fee = CMoney_Type() 
		#总冻结
		self.Total_Frozen = CMoney_Type() 
		#等于min（Total_Collateral，Curr_Margin×80％）
		self.Collateral_For_Margin = CMoney_Type() 
		#帐户状态
		self.Account_Status = CAccount_Status_Type() 

#客户合约持仓明细
class CCustomer_Detail_Position_Field:
    def __init__(self):
		#合约在系统中的编号
		self.Instrument_ID = CInstrument_ID_Type() 
		#客户在系统中的编号，编号唯一且遵循交易所制定的编码规则
		self.Customer_ID = CCustomer_ID_Type() 
		#客户在系统中的编号，编号唯一且遵循交易所制定的编码规则
		self.Customer_Trade_Code = CCustomer_Trade_Code_Type() 
		#1．买2．卖
		self.Direction = CDirection_Type() 
		#持仓的当前数量
		self.Position = CVolume_Type() 
		#持仓保证金
		self.Margin = CMoney_Type() 
		#一个交易所的编号
		self.Exchange_ID = CExchange_ID_Type() 
		#成交编号
		self.Trade_ID = CTrade_ID_Type() 
		#持仓价格
		self.Hold_Price = CPrice_Type() 
		#开仓价格
		self.Open_Price = CPrice_Type() 
		#持仓造成的盈亏金额
		self.Position_Profit = CMoney_Type() 

#客户合约持仓汇总
class CCustomer_Total_Position_Field:
    def __init__(self):
		#合约在系统中的编号
		self.Instrument_ID = CInstrument_ID_Type() 
		#客户在系统中的编号，编号唯一且遵循交易所制定的编码规则
		self.Customer_ID = CCustomer_ID_Type() 
		#客户在系统中的编号，编号唯一且遵循交易所制定的编码规则
		self.Customer_Trade_Code = CCustomer_Trade_Code_Type() 
		#1．买2．卖
		self.Direction = CDirection_Type() 
		#持仓的当前数量
		self.Position = CVolume_Type() 
		#持仓保证金
		self.Margin = CMoney_Type() 
		#持仓均价
		self.Hold_Average_Price = CPrice_Type() 
		#开仓均价
		self.Open_Average_Price = CPrice_Type() 
		#今日持仓的当前数量
		self.Today_Position = CVolume_Type() 
		#总冻结
		self.Total_Frozen = CVolume_Type() 
		#今日冻结
		self.Today_Frozen = CVolume_Type() 

#报盘机注册
class COffer_Regist_Field:
    def __init__(self):
		#一个交易所的编号
		self.Exchange_ID = CExchange_ID_Type() 
		#交易员在系统中的编号，编号唯一且遵循交易所制定的编码规则
		self.Seat_ID = CSeat_ID_Type() 
		#一个报盘机的编号
		self.Offer_ID = COffer_ID_Type() 
		#一个报盘机的名称
		self.Offer_Name = COffer_Name_Type() 
		#报盘机状态
		self.Offer_Status = COffer_Status_Type() 
		#报盘机的会话ID
		self.Offer_SessionID = COffer_SessionID_Type() 

#客户初始化状态
class CCustomer_Initial_Status_Field:
    def __init__(self):
		#会话标识
		self.Session_ID = CSession_ID_Type() 
		#初始化状态
		self.Initial_Status = CInitial_Status_Type() 

#信息查询
class CInformation_Field:
    def __init__(self):
		#编号
		self.Information_ID = CInformation_ID_Type() 
		#序列号
		self.Sequence_No = CSequence_No_Type() 
		#消息正文内容
		self.Content = CContent_Type() 
		#正文长度
		self.Content_Length = CContent_Length_Type() 
		#是否完成
		self.Is_Accomplished = CBool_Type() 

#行情订阅
class CSubscribeQuote_Field:
    def __init__(self):
		#交易所代码
		self.Exchange_ID = CExchange_ID_Type() 
		#合约代码
		self.Instrument_ID = CInstrument_ID_Type() 

#触发器操作
class CTrigger_Action_Field:
    def __init__(self):
		#操作标志
		self.Action_Flag = CTrigger_Action_Flag_Type() 
		#操作时间
		self.Active_Time = CTime_Type() 
		#触发器ID
		self.Trigger_ID = CSequence_No_Type() 

#操作日志
class COperation_Log_Field:
    def __init__(self):
		#当前日期
		self.Operation_Date = CDate_Type() 
		#时间
		self.Operation_Time = CTime_Type() 
		#操作序列号
		self.Sequence_No = CSequence_No_Type() 
		#操作员代码
		self.Operator_ID = COperator_ID_Type() 
		#操作类型
		self.Operation_Type = COperation_Type_Type() 
		#操作摘要
		self.Operation_Desc = CContent_Type() 
		#操作摘要
		self.Operation_Result = CContent_Type() 

#交易所时间
class CExchange_Time_Field:
    def __init__(self):
		#一个交易所的编号
		self.Exchange_ID = CExchange_ID_Type() 
		#交易所名称
		self.Exchange_Name = CExchange_Name_Type() 
		#操作序列号
		self.Sequence_No = CSequence_No_Type() 
		#当前日期（年）
		self.Curr_Year = CYear_Type() 
		#当前时间（月份）
		self.Curr_Month = CMonth_Type() 
		#当前时间（日期）
		self.Curr_Day = CDay_Type() 
		#当前日期（小时）
		self.Curr_Hour = CHour_Type() 
		#当前日期（分钟）
		self.Curr_Minute = CMinute_Type() 
		#当前时间（秒）
		self.Curr_Second = CSecond_Type() 
		#当前时间（毫秒）
		self.Curr_Millisec = CMillisec_Type() 
		#相对时间
		self.Relative_Time = CSerial_No_Type() 

#报单查询
class CQry_Order_Field:
    def __init__(self):
		#报单编号
		self.Order_Sys_ID = COrder_Sys_ID_Type() 
		#合约代码
		self.Instrument_ID = CInstrument_ID_Type() 
		#客户代码
		self.Customer_ID = CCustomer_ID_Type() 

#成交查询
class CQry_Trade_Field:
    def __init__(self):
		#起始合约代码
		self.Inst_ID_Start = CInstrument_ID_Type() 
		#结束合约代码
		self.Inst_ID_End = CInstrument_ID_Type() 
		#成交编号
		self.Trade_ID = CTrade_ID_Type() 
		#客户代码
		self.Customer_ID = CCustomer_ID_Type() 

#行情查询
class CQry_Market_Data_Field:
    def __init__(self):
		#合约代码
		self.Instrument_ID = CInstrument_ID_Type() 

#客户持仓查询
class CQry_Customer_Position_Field:
    def __init__(self):
		#客户代码
		self.Customer_ID = CCustomer_ID_Type() 
		#起始合约代码
		self.Inst_ID_Start = CInstrument_ID_Type() 
		#结束合约代码
		self.Inst_ID_End = CInstrument_ID_Type() 

#交易资金查询
class CQry_Account_Field:
    def __init__(self):
		#客户代码
		self.Customer_ID = CCustomer_ID_Type() 
		#资金帐号
		self.Account_ID = CAccount_ID_Type() 

#合约查询
class CQry_Instrument_Field:
    def __init__(self):
		#交易所代码
		self.Exchange_ID = CExchange_ID_Type() 
		#合约代码
		self.Instrument_ID = CInstrument_ID_Type() 
		#客户代码
		self.Customer_ID = CCustomer_ID_Type() 

#交易所状态查询
class CQry_Exchange_Status_Field:
    def __init__(self):
		#交易所代码
		self.Exchange_ID = CExchange_ID_Type() 

#合约价位查询
class CQry_MBLMarket_Data_Field:
    def __init__(self):
		#交易所代码
		self.Exchange_ID = CExchange_ID_Type() 
		#合约代码
		self.Instrument_ID = CInstrument_ID_Type() 

#查询客户
class CQry_Customer_Field:
    def __init__(self):
		#起始客户代码
		self.Customer_ID_Start = CCustomer_ID_Type() 
		#结束客户代码
		self.Customer_ID_End = CCustomer_ID_Type() 

#查询客户应答
class CQry_Rsp_Customer_Field:
    def __init__(self):
		#客户在系统中的编号，编号唯一且遵循交易所制定的编码规则
		self.Customer_ID = CCustomer_ID_Type() 
		#客户名称
		self.Customer_Name = CParty_Name_Type() 
		#自然人，法人
		self.Customer_Type = CCustomer_Type_Type() 
		#密码
		self.Password = CPassword_Type() 
		#客户端的报单ID，系统只是记录并返回，不处理该字段
		self.Customer_Order_Local_ID = COrder_Local_ID_Type() 
		#正常，只可平仓，禁止交易
		self.Customer_Status = CCustomer_Status_Type() 

#信息查询
class CQry_Information_Field:
    def __init__(self):
		#起始信息代码
		self.Information_ID_Start = CInformation_ID_Type() 
		#结束信息代码
		self.Information_ID_End = CInformation_ID_Type() 

#触发报单查询
class CQry_Trigger_Order_Field:
    def __init__(self):
		#报单指令类型
		self.Order_Local_Instruction_Type = COrder_Local_Instruction_Type_Type() 
		#报单指令编码
		self.Order_Local_Instruction_ID = COrder_Local_Instruction_ID_Type() 
		#客户代码
		self.Customer_ID = CCustomer_ID_Type() 

#合约属性
class CCurr_Instrument_Property_Field:
    def __init__(self):
		#市场价报单的最大下单量
		self.Max_Market_Order_Volume = CVolume_Type() 
		#市场价报单的最小下单量
		self.Min_Market_Order_Volume = CVolume_Type() 
		#限价报单的最大下单量
		self.Max_Limit_Order_Volume = CVolume_Type() 
		#限价报单的最小下单量
		self.Min_Limit_Order_Volume = CVolume_Type() 
		#最大持仓量
		self.Max_Limit_Position_Volume = CVolume_Type() 
		#合约的单位价格涨跌变化的最小值
		self.Price_Tick = CPrice_Type() 

#当前合约费率
class CInstrument_Rate_Field:
    def __init__(self):
		#保证金率
		self.Margin_Rate = CRatio_Type() 
		#手续费率
		self.Fee_Rate = CRatio_Type() 
		#平今手续费
		self.Offset_Today_Rate = CRatio_Type() 

#市场行情
class CMarket_Data_Field:
    def __init__(self):
		#当日该合约交易期间的最新成交价格
		self.Last_Price = CPrice_Type() 
		#上一日的结算价
		self.Pre_Settlement_Price = CPrice_Type() 
		#上一日收盘价
		self.Pre_Close_Price = CPrice_Type() 
		#前最后持仓量，双向计算
		self.Pre_Open_Interest = CLarge_Volume_Type() 
		#该期货合约开市前五分钟内经集合竞价产生的成交价格
		self.Open_Price = CPrice_Type() 
		#指一定时间内该合约成交价中的最高成交价格
		self.Highest_Price = CPrice_Type() 
		#指一定时间内该合约成交价中的最低成交价格
		self.Lowest_Price = CPrice_Type() 
		#该合约在当日交易期价所有成交合约的双边数量
		self.Volume = CVolume_Type() 
		#该合约完成交易的市值
		self.Turnover = CMoney_Type() 
		#最后持仓量，双向计算
		self.Open_Interest = CLarge_Volume_Type() 
		#该合约当日交易的最后一笔成交价格
		self.Close_Price = CPrice_Type() 
		#该合约当日成交价格按成交量的加权平均价，当日无成交的，按上一日结算价
		self.Settlement_Price = CPrice_Type() 
		#涨停板价
		self.Upper_Limit_Price = CPrice_Type() 
		#跌停板价
		self.Lower_Limit_Price = CPrice_Type() 
		#最后修改时间
		self.Update_Time = CTime_Type() 
		#最后修改毫秒
		self.Update_Millisec = CMillisec_Type() 
		#一个交易所的编号
		self.Exchange_ID = CExchange_ID_Type() 
		#合约在系统中的编号
		self.Instrument_ID = CInstrument_ID_Type() 

#深度行情
class CDepth_Market_Data_Field:
    def __init__(self):
		#当日该合约交易期间的最新成交价格
		self.Last_Price = CPrice_Type() 
		#上一日的结算价
		self.Pre_Settlement_Price = CPrice_Type() 
		#上一日收盘价
		self.Pre_Close_Price = CPrice_Type() 
		#前最后持仓量，双向计算
		self.Pre_Open_Interest = CLarge_Volume_Type() 
		#该期货合约开市前五分钟内经集合竞价产生的成交价格
		self.Open_Price = CPrice_Type() 
		#指一定时间内该合约成交价中的最高成交价格
		self.Highest_Price = CPrice_Type() 
		#指一定时间内该合约成交价中的最低成交价格
		self.Lowest_Price = CPrice_Type() 
		#该合约在当日交易期价所有成交合约的双边数量
		self.Volume = CVolume_Type() 
		#该合约完成交易的市值
		self.Turnover = CMoney_Type() 
		#最后持仓量，双向计算
		self.Open_Interest = CLarge_Volume_Type() 
		#该合约当日交易的最后一笔成交价格
		self.Close_Price = CPrice_Type() 
		#该合约当日成交价格按成交量的加权平均价，当日无成交的，按上一日结算价
		self.Settlement_Price = CPrice_Type() 
		#涨停板价
		self.Upper_Limit_Price = CPrice_Type() 
		#跌停板价
		self.Lower_Limit_Price = CPrice_Type() 
		#最后修改时间
		self.Update_Time = CTime_Type() 
		#最后修改毫秒
		self.Update_Millisec = CMillisec_Type() 
		#一个交易所的编号
		self.Exchange_ID = CExchange_ID_Type() 
		#合约在系统中的编号
		self.Instrument_ID = CInstrument_ID_Type() 
		#该合约当日交易所交易系统中未成交的申请买入最高价位
		self.Bid_Price1 = CPrice_Type() 
		#该合约当日交易所交易系统中未成交的最高价位申请买入的下单数
		self.Bid_Volume1 = CVolume_Type() 
		#该合约当日交易所交易系统中未成交的申请卖出最低价位
		self.Ask_Price1 = CPrice_Type() 
		#该合约当日交易所交易系统中未成交的最低价位申请卖出的下单数
		self.Ask_Volume1 = CVolume_Type() 
		#该合约当日交易所交易系统中未成交的申请买入最高价位
		self.Bid_Price2 = CPrice_Type() 
		#该合约当日交易所交易系统中未成交的最高价位申请买入的下单数
		self.Bid_Volume2 = CVolume_Type() 
		#该合约当日交易所交易系统中未成交的申请卖出最低价位
		self.Ask_Price2 = CPrice_Type() 
		#该合约当日交易所交易系统中未成交的最低价位申请卖出的下单数
		self.Ask_Volume2 = CVolume_Type() 
		#该合约当日交易所交易系统中未成交的申请买入最高价位
		self.Bid_Price3 = CPrice_Type() 
		#该合约当日交易所交易系统中未成交的最高价位申请买入的下单数
		self.Bid_Volume3 = CVolume_Type() 
		#该合约当日交易所交易系统中未成交的申请卖出最低价位
		self.Ask_Price3 = CPrice_Type() 
		#该合约当日交易所交易系统中未成交的最低价位申请卖出的下单数
		self.Ask_Volume3 = CVolume_Type() 
		#该合约当日交易所交易系统中未成交的申请买入最高价位
		self.Bid_Price4 = CPrice_Type() 
		#该合约当日交易所交易系统中未成交的最高价位申请买入的下单数
		self.Bid_Volume4 = CVolume_Type() 
		#该合约当日交易所交易系统中未成交的申请卖出最低价位
		self.Ask_Price4 = CPrice_Type() 
		#该合约当日交易所交易系统中未成交的最低价位申请卖出的下单数
		self.Ask_Volume4 = CVolume_Type() 
		#该合约当日交易所交易系统中未成交的申请买入最高价位
		self.Bid_Price5 = CPrice_Type() 
		#该合约当日交易所交易系统中未成交的最高价位申请买入的下单数
		self.Bid_Volume5 = CVolume_Type() 
		#该合约当日交易所交易系统中未成交的申请卖出最低价位
		self.Ask_Price5 = CPrice_Type() 
		#该合约当日交易所交易系统中未成交的最低价位申请卖出的下单数
		self.Ask_Volume5 = CVolume_Type() 

#分价表
class CMBL_Market_Data_Field:
    def __init__(self):
		#合约代码
		self.Instrument_ID = CInstrument_ID_Type() 
		#买卖方向
		self.Direction = CDirection_Type() 
		#价格
		self.Price = CPrice_Type() 
		#数量
		self.Volume = CVolume_Type() 

#行情基础属性
class CMarket_Data_Base_Field:
    def __init__(self):
		#交易日
		self.Trading_Day = CDate_Type() 
		#昨结算
		self.Pre_Settlement_Price = CPrice_Type() 
		#昨收盘
		self.Pre_Close_Price = CPrice_Type() 
		#昨持仓量
		self.Pre_Open_Interest = CLarge_Volume_Type() 
		#昨虚实度
		self.Pre_Delta = CRatio_Type() 

#行情静态属性
class CMarket_Data_Static_Field:
    def __init__(self):
		#今开盘
		self.Open_Price = CPrice_Type() 
		#最高价
		self.Highest_Price = CPrice_Type() 
		#最低价
		self.Lowest_Price = CPrice_Type() 
		#今收盘
		self.Close_Price = CPrice_Type() 
		#涨停板价
		self.Upper_Limit_Price = CPrice_Type() 
		#跌停板价
		self.Lower_Limit_Price = CPrice_Type() 
		#今结算
		self.Settlement_Price = CPrice_Type() 
		#今虚实度
		self.Curr_Delta = CRatio_Type() 
		#历史最高价
		self.Life_Hight = CPrice_Type() 
		#历史最低价
		self.Life_Low = CPrice_Type() 

#行情最新成交属性
class CMarket_Data_Last_Match_Field:
    def __init__(self):
		#最新价
		self.Last_Price = CPrice_Type() 
		#最新成交量
		self.Last_Match_Volume = CVolume_Type() 
		#成交金额
		self.Turnover = CMoney_Type() 
		#成交量
		self.Total_Match_Volume = CVolume_Type() 
		#持仓量
		self.Open_Interest = CLarge_Volume_Type() 
		#持仓量变化
		self.Interest_Change = CVolume_Type() 
		#当日均价
		self.Average_Price = CPrice_Type() 

#行情最优价属性
class CMarket_Data_Best_Price_Field:
    def __init__(self):
		#申买价一
		self.Bid_Price1 = CPrice_Type() 
		#申买量一
		self.Bid_Volume1 = CVolume_Type() 
		#申卖价一
		self.Ask_Price1 = CPrice_Type() 
		#申卖量一
		self.Ask_Volume1 = CVolume_Type() 

#行情申买二_三属性
class CMarket_Data_Bid23_Field:
    def __init__(self):
		#申买价二
		self.Bid_Price2 = CPrice_Type() 
		#申买量二
		self.Bid_Volume2 = CVolume_Type() 
		#申买价三
		self.Bid_Price3 = CPrice_Type() 
		#申买量三
		self.Bid_Volume3 = CVolume_Type() 

#行情申卖二_三属性
class CMarket_Data_Ask23_Field:
    def __init__(self):
		#申卖价二
		self.Ask_Price2 = CPrice_Type() 
		#申卖量二
		self.Ask_Volume2 = CVolume_Type() 
		#申卖价三
		self.Ask_Price3 = CPrice_Type() 
		#申卖量三
		self.Ask_Volume3 = CVolume_Type() 

#行情申买四_五属性
class CMarket_Data_Bid45_Field:
    def __init__(self):
		#申买价四
		self.Bid_Price4 = CPrice_Type() 
		#申买量四
		self.Bid_Volume4 = CVolume_Type() 
		#申买价五
		self.Bid_Price5 = CPrice_Type() 
		#申买量五
		self.Bid_Volume5 = CVolume_Type() 

#行情申卖四_五属性
class CMarket_Data_Ask45_Field:
    def __init__(self):
		#申卖价四
		self.Ask_Price4 = CPrice_Type() 
		#申卖量四
		self.Ask_Volume4 = CVolume_Type() 
		#申卖价五
		self.Ask_Price5 = CPrice_Type() 
		#申卖量五
		self.Ask_Volume5 = CVolume_Type() 

#行情更新时间属性
class CMarket_Data_Update_Time_Field:
    def __init__(self):
		#合约代码
		self.Instrument_ID = CInstrument_ID_Type() 
		#最后修改时间
		self.Update_Time = CTime_Type() 
		#最后修改毫秒
		self.Update_Millisec = CMillisec_Type() 

#分价项
class CShort_MBL_Market_Data_Field:
    def __init__(self):
		#买卖方向
		self.Direction = CDirection_Type() 
		#价格
		self.Price = CPrice_Type() 
		#数量
		self.Volume = CVolume_Type() 

#客户合约
class CCustomer_Instrument_Field:
    def __init__(self):
		#品种在系统中的编号
		self.Variety_ID = CVariety_ID_Type() 
		#表明合约的持仓类型
		self.Position_Type = CPosition_Type_Type() 
		#品种的每手交易的规定数量，针对基础的商品
		self.Volume_Multiple = CVolume_Multiple_Type() 
		#一个交易所的编号
		self.Exchange_ID = CExchange_ID_Type() 
		#合约在系统中的编号
		self.Instrument_ID = CInstrument_ID_Type() 
		#合约的名称
		self.Instrument_Name = CInstrument_Name_Type() 
		#该合约规定进行实物交割的年份
		self.Delivery_Year = CYear_Type() 
		#该合约规定进行实物交割的月份
		self.Delivery_Month = CMonth_Type() 
		#市场价报单的最大下单量
		self.Max_Market_Order_Volume = CVolume_Type() 
		#市场价报单的最小下单量
		self.Min_Market_Order_Volume = CVolume_Type() 
		#限价报单的最大下单量
		self.Max_Limit_Order_Volume = CVolume_Type() 
		#限价报单的最小下单量
		self.Min_Limit_Order_Volume = CVolume_Type() 
		#最大持仓量
		self.Max_Limit_Position_Volume = CVolume_Type() 
		#合约的单位价格涨跌变化的最小值
		self.Price_Tick = CPrice_Type() 
		#保证金率
		self.Margin_Rate = CRatio_Type() 
		#手续费率
		self.Fee_Rate = CRatio_Type() 
		#平今手续费
		self.Offset_Today_Rate = CRatio_Type() 
		#客户在系统中的编号，编号唯一且遵循交易所制定的编码规则
		self.Customer_ID = CCustomer_ID_Type() 

#客户出入金
class CCustomer_IO_Money_Field:
    def __init__(self):
		#出入金流水号
		self.Money_IO_Sequence_No = CSequence_String_Type() 
		#客户在系统中的编号，编号唯一且遵循交易所制定的编码规则
		self.Customer_ID = CCustomer_ID_Type() 
		#柜台收到报文的日期
		self.Receive_Date = CDate_Type() 
		#柜台收到报文的时间
		self.Receive_Time = CTime_Type() 
		#入金
		self.Money_In = CMoney_Type() 
		#出金
		self.Money_Out = CMoney_Type() 
		#备注
		self.Comment = CContent_Type() 
		#上场状态
		self.Status = CMoney_IO_Up_Status_Type() 

