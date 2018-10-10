#ifndef __CONST_DEFINE_H__
#define __CONST_DEFINE_H__

/////////////////////////////////////////////////////////////////////////////////////////
//////////////////////业务常量///////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////
///正常
#define CN_CS_Normal '0'
///只可平仓
#define CN_CS_Only_Close '1'
///不可交易
#define CN_CS_Stop '2'

///未上市
#define CN_IP_Not_Start '0'
///上市
#define CN_IP_Started '1'
///停牌
#define CN_IP_Pause '2'
///到期
#define CN_IP_Expired '3'

///非期权
#define CN_OT_NotOptions '0'
///看涨
#define CN_OT_CallOptions '1'
///看跌
#define CN_OT_PutOptions '2'

///净
#define CN_PD_Net '1'
///多头
#define CN_PD_Long '2'
///空头
#define CN_PD_Short '3'

///开盘前
#define CN_IS_Before_Trading '0'
///非交易
#define CN_IS_No_Trading '1'
///连续交易
#define CN_IS_Continous '2'
///集合竞价报单
#define CN_IS_Auction_Ordering '3'
///集合竞价价格平衡
#define CN_IS_Auction_Balance '4'
///集合竞价撮合
#define CN_IS_Auction_Match '5'
///收盘
#define CN_IS_Closed '6'

///买
#define CN_D_Buy '0'
///卖
#define CN_D_Sell '1'

///投机
#define CN_HF_NULL '1'
///保值
#define CN_HF_Hedge '3'

///强平
#define CN_PS_Force '0'
///一般
#define CN_PS_Normal '1'

///撤消
#define CN_AF_Cancel '0'
///修改
#define CN_AF_Modify '1'

///开始
#define CN_TAF_START '0'
///结束
#define CN_TAF_STOP '1'

///净持仓
#define CN_PT_Net '1'
///综合持仓
#define CN_PT_Gross '2'

///活跃
#define CN_ES_Active '1'
///不活跃
#define CN_ES_Non_Active '2'

///动态
#define CN_PL_Dynamic '1'
///静态
#define CN_PL_Static '2'

///无
#define CN_VM_None '0'
///百分比
#define CN_VM_Percentage '1'
///绝对值
#define CN_VM_Absolute '2'

///舍出
#define CN_RM_Out '1'
///四舍五入
#define CN_RM_Round '2'
///舍入
#define CN_RM_In '3'
///截断
#define CN_RM_Trunc '4'

///入金
#define CN_AT_Deposit '1'
///出金
#define CN_AT_Withdraw '2'
///手续费
#define CN_AT_Fee '3'

///直接报单
#define CN_CIT_Normal_Type '1'
///自动撤销
#define CN_CIT_AutoCancel_Type '2'
///自动拆单
#define CN_CIT_AutoSplit_Type '3'
///多次发送
#define CN_CIT_MultiSend_Type '4'
///时间检测
#define CN_CIT_DetectTime_Type '5'

///任意价
#define CN_OPT_Any_Price '1'
///限价
#define CN_OPT_Limit_Price '2'
///最优价
#define CN_OPT_Best_Price '3'

///开仓
#define CN_OF_Open '0'
///平仓
#define CN_OF_Close '1'
///强平
#define CN_OF_Force_Close '2'
///平今
#define CN_OF_Close_Today '3'
///平昨
#define CN_OF_Close_Yesterday '4'

///全部成交
#define CN_OST_All_Traded '0'
///部分成交还在队列中
#define CN_OST_Part_Traded_Queueing '1'
///部分成交不在队列中
#define CN_OST_Part_Traded_Not_Queueing '2'
///未成交还在队列中
#define CN_OST_No_Trade_Queueing '3'
///未成交不在队列中
#define CN_OST_No_Trade_Not_Queueing '4'
///撤单
#define CN_OST_Canceled '5'
///未知
#define CN_OST_Unknown 'a'
///尚未触发
#define CN_OST_NotTouched 'b'
///已触发
#define CN_OST_Touched 'c'

///立即完成_否则撤销
#define CN_TC_IOC '1'
///本节有效
#define CN_TC_GFS '2'
///当日有效
#define CN_TC_GFD '3'
///指定日期前有效
#define CN_TC_GTD '4'
///撤销前有效
#define CN_TC_GTC '5'
///集合竞价有效
#define CN_TC_GFA '6'

///任何数量
#define CN_VC_AV '1'
///最小数量
#define CN_VC_MV '2'
///全部数量
#define CN_VC_CV '3'

///立即
#define CN_CC_Immediately '1'
///止损
#define CN_CC_Touch '2'

///用户
#define CN_AS_User '0'
///内部
#define CN_AS_Internal '1'
///管理员
#define CN_AS_Administrator '2'

///可以交易
#define CN_TR_Allow '0'
///只能平仓
#define CN_TR_Close_Only '1'
///不能交易
#define CN_TR_Forbidden '2'

///价格优先时间优先
#define CN_TM_Price_Time '0'
///价格优先按比例分配
#define CN_TM_Prorata '1'

///来自参与者
#define CN_OSRC_Participant '0'
///来自管理员
#define CN_OSRC_Administrator '1'

///激活状态
#define CN_ACCS_Enable '0'
///停止状态
#define CN_ACCS_Disable '1'

///期货
#define CN_ACCT_Domestic_Future '0'
///现货
#define CN_ACCT_Domestic_Stock '1'
///期货
#define CN_ACCT_international_Future '2'

///主键
#define CN_IK_Key 'T'
///非主键
#define CN_IK_Not_Key 'F'

///字段为空
#define CN_IN_Null 'T'
///字段非空
#define CN_IN_Not_Null 'F'

///未连接
#define CN_OS_Not_Connected '0'
///连接未工作
#define CN_OS_Connected_Not_Work '1'
///正常工作
#define CN_OS_Work '2'

///上场未确认
#define CN_MIUS_Not_Confirm '0'
///上场已确认
#define CN_MIUS_Confirm_OK '1'
///上场失败
#define CN_MIUS_Confirm_Error '2'

///登录
#define CN_OT_Login '0'
///登出
#define CN_OT_Logout '1'
///操作
#define CN_OT_Operate '2'

///行情
#define CN_AT_Quote '0'
///交易
#define CN_AT_Trade '1'

///订阅
#define CN_SO_Subscribe '1'
///退订
#define CN_SO_Unsubscribe '0'

///开始连接
#define CN_TCS_Start_Connect '0'
///连接成功
#define CN_TCS_Connected '1'
///连接断开
#define CN_TCS_Lose_Connect '2'

///期货
#define CN_VC_Futures '1'
///期权
#define CN_VC_Options '2'
///组合
#define CN_VC_Combination '3'
///即期
#define CN_VC_Spot '4'
///期转现
#define CN_VC_EFP '5'

///跨期
#define CN_CT_Spread '0'
///跨品种
#define CN_CT_Spread_Variety '1'
///压榨套利
#define CN_CT_Crush_Spread '2'
///展期
#define CN_CT_Extension '3'

///一般单腿
#define CN_OT_Normal_Single '0'
///多腿组合
#define CN_OT_Combination '1'
///检测单腿
#define CN_OT_Detect_Single '8'
///测试单腿
#define CN_OT_Test_Single '9'

///正常
#define CN_RM_Normal '0'
///高速
#define CN_RM_High_Speed '1'

///准备
#define CN_DAT_Prepare '0'
///开始
#define CN_DAT_Start '1'
///结束
#define CN_DAT_End '2'

///未对时
#define CN_DTS_Not_Detect '0'
///对时失败
#define CN_DTS_Detect_Faild '1'
///对时成功
#define CN_DTS_Detect_Ok '2'


/////////////////////////////////////////////////////////////////////////////////////////
//////////////////////服务号定义/////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////
#define  MANAGE_SERVER_ID             1000  //管理服务
#define  RISK_SERVER_ID               2000  //盘中风控服务


/////////////////////////////////////////////////////////////////////////////////////////
//////////////////////管理端相关指令///////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////
#define MANAGE_USER_LOGIN_COMMAND           1            //管理用户登陆
#define MANAGE_USER_LOGOUT_COMMAND          2            //管理用户登出
#define TRADER_USER_LOGIN_COMMAND           3            //交易用户登陆
#define TRADER_USER_LOGOUT_COMMAND          4            //交易用户登出

// 交易所表操作
#define ADD_ST_EXCHANGE_COMMAND		5  //增加[交易所表]
#define DEL_ST_EXCHANGE_COMMAND		6  //删除[交易所表]
#define UPD_ST_EXCHANGE_COMMAND		7  //修改[交易所表]
#define QRY_ST_EXCHANGE_COMMAND		8  //查询[交易所表]

// 合约状态表操作
#define ADD_ST_INSTRUMENT_STATUS_COMMAND		9  //增加[合约状态表]
#define DEL_ST_INSTRUMENT_STATUS_COMMAND		10  //删除[合约状态表]
#define UPD_ST_INSTRUMENT_STATUS_COMMAND		11  //修改[合约状态表]
#define QRY_ST_INSTRUMENT_STATUS_COMMAND		12  //查询[合约状态表]

// 合约表操作
#define ADD_ST_INSTRUMENT_COMMAND		13  //增加[合约表]
#define DEL_ST_INSTRUMENT_COMMAND		14  //删除[合约表]
#define UPD_ST_INSTRUMENT_COMMAND		15  //修改[合约表]
#define QRY_ST_INSTRUMENT_COMMAND		16  //查询[合约表]

// 合约保证金手续费表操作
#define ADD_ST_INSTRUMENT_COMMISSION_MARGIN_COMMAND		17  //增加[合约保证金手续费表]
#define DEL_ST_INSTRUMENT_COMMISSION_MARGIN_COMMAND		18  //删除[合约保证金手续费表]
#define UPD_ST_INSTRUMENT_COMMISSION_MARGIN_COMMAND		19  //修改[合约保证金手续费表]
#define QRY_ST_INSTRUMENT_COMMISSION_MARGIN_COMMAND		20  //查询[合约保证金手续费表]

// 合约固定手续费保证金表操作
#define ADD_ST_FIX_INSTRUMENT_COMMISSION_MARGIN_COMMAND		21  //增加[合约固定手续费保证金表]
#define DEL_ST_FIX_INSTRUMENT_COMMISSION_MARGIN_COMMAND		22  //删除[合约固定手续费保证金表]
#define UPD_ST_FIX_INSTRUMENT_COMMISSION_MARGIN_COMMAND		23  //修改[合约固定手续费保证金表]
#define QRY_ST_FIX_INSTRUMENT_COMMISSION_MARGIN_COMMAND		24  //查询[合约固定手续费保证金表]

// 最优行情操作
#define ADD_ST_BEST_MARKET_DATA_COMMAND		25  //增加[最优行情]
#define DEL_ST_BEST_MARKET_DATA_COMMAND		26  //删除[最优行情]
#define UPD_ST_BEST_MARKET_DATA_COMMAND		27  //修改[最优行情]
#define QRY_ST_BEST_MARKET_DATA_COMMAND		28  //查询[最优行情]

// 委托表操作
#define ADD_ST_ORDER_COMMAND		29  //增加[委托表]
#define DEL_ST_ORDER_COMMAND		30  //删除[委托表]
#define UPD_ST_ORDER_COMMAND		31  //修改[委托表]
#define QRY_ST_ORDER_COMMAND		32  //查询[委托表]

// 成交表操作
#define ADD_ST_TRADE_COMMAND		33  //增加[成交表]
#define DEL_ST_TRADE_COMMAND		34  //删除[成交表]
#define UPD_ST_TRADE_COMMAND		35  //修改[成交表]
#define QRY_ST_TRADE_COMMAND		36  //查询[成交表]

// 持仓汇总表操作
#define ADD_ST_POSITION_COMMAND		37  //增加[持仓汇总表]
#define DEL_ST_POSITION_COMMAND		38  //删除[持仓汇总表]
#define UPD_ST_POSITION_COMMAND		39  //修改[持仓汇总表]
#define QRY_ST_POSITION_COMMAND		40  //查询[持仓汇总表]

// 资金信息表操作
#define ADD_ST_MONEY_COMMAND		41  //增加[资金信息表]
#define DEL_ST_MONEY_COMMAND		42  //删除[资金信息表]
#define UPD_ST_MONEY_COMMAND		43  //修改[资金信息表]
#define QRY_ST_MONEY_COMMAND		44  //查询[资金信息表]

// 管理员表操作
#define ADD_ST_MANAGE_USER_COMMAND		45  //增加[管理员表]
#define DEL_ST_MANAGE_USER_COMMAND		46  //删除[管理员表]
#define UPD_ST_MANAGE_USER_COMMAND		47  //修改[管理员表]
#define QRY_ST_MANAGE_USER_COMMAND		48  //查询[管理员表]

// 交易员表操作
#define ADD_ST_TRADE_USER_COMMAND		49  //增加[交易员表]
#define DEL_ST_TRADE_USER_COMMAND		50  //删除[交易员表]
#define UPD_ST_TRADE_USER_COMMAND		51  //修改[交易员表]
#define QRY_ST_TRADE_USER_COMMAND		52  //查询[交易员表]

// 用户登录信息表操作
#define ADD_ST_USER_LOGIN_COMMAND		53  //增加[用户登录信息表]
#define DEL_ST_USER_LOGIN_COMMAND		54  //删除[用户登录信息表]
#define UPD_ST_USER_LOGIN_COMMAND		55  //修改[用户登录信息表]
#define QRY_ST_USER_LOGIN_COMMAND		56  //查询[用户登录信息表]

// 交易员代理策略表操作
#define ADD_ST_TRADER_BROKER_STRATEGY_COMMAND		57  //增加[交易员代理策略表]
#define DEL_ST_TRADER_BROKER_STRATEGY_COMMAND		58  //删除[交易员代理策略表]
#define UPD_ST_TRADER_BROKER_STRATEGY_COMMAND		59  //修改[交易员代理策略表]
#define QRY_ST_TRADER_BROKER_STRATEGY_COMMAND		60  //查询[交易员代理策略表]

// 策略参数表操作
#define ADD_ST_STRATEGY_PARA_COMMAND		61  //增加[策略参数表]
#define DEL_ST_STRATEGY_PARA_COMMAND		62  //删除[策略参数表]
#define UPD_ST_STRATEGY_PARA_COMMAND		63  //修改[策略参数表]
#define QRY_ST_STRATEGY_PARA_COMMAND		64  //查询[策略参数表]

// 结算价表操作
#define ADD_ST_CLOSE_PRICE_COMMAND		65  //增加[结算价表]
#define DEL_ST_CLOSE_PRICE_COMMAND		66  //删除[结算价表]
#define UPD_ST_CLOSE_PRICE_COMMAND		67  //修改[结算价表]
#define QRY_ST_CLOSE_PRICE_COMMAND		68  //查询[结算价表]

// 交易日历表操作
#define ADD_ST_TRADE_CALENDAR_COMMAND		69  //增加[交易日历表]
#define DEL_ST_TRADE_CALENDAR_COMMAND		70  //删除[交易日历表]
#define UPD_ST_TRADE_CALENDAR_COMMAND		71  //修改[交易日历表]
#define QRY_ST_TRADE_CALENDAR_COMMAND		72  //查询[交易日历表]

// 交易参数表操作
#define ADD_ST_TRADE_PARA_COMMAND		73  //增加[交易参数表]
#define DEL_ST_TRADE_PARA_COMMAND		74  //删除[交易参数表]
#define UPD_ST_TRADE_PARA_COMMAND		75  //修改[交易参数表]
#define QRY_ST_TRADE_PARA_COMMAND		76  //查询[交易参数表]


/////////////////////////////////////////////////////////////////////////////////////////
//////////////////////交易相关指令///////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////
#define TRADE_MARKET_CONNECTED_COMMAND		77  //行情连接成功   
#define TRADE_MARKET_DISCONNECT_COMMAND		78  //行情连接失败   
#define TRADE_RTN_MARKET_DATA_COMMAND		79  //深度行情通知   
#define TRADE_OFFER_AVAILABLE_COMMAND		80  //报盘可用
#define TRADE_OFFER_UNAVAILABLE_COMMAND		81  //报盘不可用   
#define TRADE_RSP_INSERT_ORDER_COMMAND		82  //报单应答   
#define TRADE_RSP_ORDER_ACTION_COMMAND		83  //报单操作应答   
#define TRADE_RTN_ORDER_COMMAND		84  //报单回报   
#define TRADE_RTN_TRADE_COMMAND		85  //成交回报   
#define TRADE_RTN_INSTRUMENT_STATUS_COMMAND		86  //合约状态通知   
#define TRADE_RSP_QRY_INSTRUMENT_COMMAND		87  //合约查询应答   
#define TRADE_REQ_ORDER_INSERT_COMMAND		88  //报单请求   
#define TRADE_REQ_ORDER_ACTION_COMMAND		89  //报单操作请求   
#define TRADE_CHANGE_STRATEGY_PARAM		90  //调整策略参数   
#define TRADE_RTN_MONERY_COMMAND		91  //资金通知   
#define TRADE_RTN_POSITION_COMMAND		92  //持仓汇总通知   

/////////////////////////////////////////////////////////////////////////////////////////
//////////////////////结构体FIELD编号////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////
#define ST_RSP_INFO_FIELD		1  //应答信息域
#define ST_EXCHANGE_FIELD		2  //交易所表域
#define ST_INSTRUMENT_STATUS_FIELD		3  //合约状态表域
#define ST_INSTRUMENT_FIELD		4  //合约表域
#define ST_INSTRUMENT_COMMISSION_MARGIN_FIELD		5  //合约保证金手续费表域
#define ST_FIX_INSTRUMENT_COMMISSION_MARGIN_FIELD		6  //合约固定手续费保证金表域
#define ST_BEST_MARKET_DATA_FIELD		7  //最优行情域
#define ST_ORDER_FIELD		8  //委托表域
#define ST_TRADE_FIELD		9  //成交表域
#define ST_POSITION_FIELD		10  //持仓汇总表域
#define ST_MONEY_FIELD		11  //资金信息表域
#define ST_MANAGE_USER_FIELD		12  //管理员表域
#define ST_TRADE_USER_FIELD		13  //交易员表域
#define ST_USER_LOGIN_FIELD		14  //用户登录信息表域
#define ST_TRADER_BROKER_STRATEGY_FIELD		15  //交易员代理策略表域
#define ST_STRATEGY_PARA_FIELD		16  //策略参数表域
#define ST_CLOSE_PRICE_FIELD		17  //结算价表域
#define ST_TRADE_CALENDAR_FIELD		18  //交易日历表域
#define ST_TRADE_PARA_FIELD		19  //交易参数表域

#endif
