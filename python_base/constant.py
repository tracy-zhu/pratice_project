# encoding: UTF-8
# 该文件用来保存常量
import xml.dom.minidom

# G_TICK_QUOTE_FILE_ROOT_FOLDER = "\\\\192.168.1.203\\quote_server_bak\\Quote_Data\\Tick_Quote"
G_TICK_QUOTE_FILE_ROOT_FOLDER = "Z:\\"
DEPTH_QUOTE_FILE_ROOT_FILE_FOLDER = 'E:\\quote_data\\depth_quote\\'
DEPTH_QUOTE_AFTER_AUCTION_FILE_ROOT_FILE_FOLDER = 'E:\\quote_data\\depth_quote_after_auction\\'
ONE_MINUTE_QUOTE_FILE_FOLDER = 'E:\\quote_data\\1M_K\\'
G_TICK_COLUMNS = ['Instrument_ID', 'Update_Time', 'Update_Millisec', 'Trading_Day', 'Pre_Settlement_Price',
                  'Pre_Close_Price', 'Pre_Open_Interest', 'Pre_Delta', 'Open_Price', 'Highest_Price', 'Lowest_Price',
                  'Close_Price', 'Upper_Limit_Price', 'Lower_Limit_Price', 'Settlement_Price', 'Curr_Delta',
                  'Life_High', 'Life_Low', 'Last_Price', 'Last_Match_Volume', 'Turnover', 'Total_Match_Volume',
                  'Open_Interest', 'Interest_Change', 'Average_Price', 'Bid_Price1', 'Bid_Volume1', 'Ask_Price1',
                  'Ask_Volume1', 'Exchange_ID']
MINUTE_COLUMNS = ['Instrument_ID', 'Update_Time', 'open_price', 'high_price', 'low_price', 'close_price',
                  'trade_volume', 'total_position']
TRADE_PHASE_FILE_NAME = "F:\\tool\\trade_phase\\20160503-99999999_trade_phase.xml"
TRADING_DAY_LIST_FILE_NAME = "F:\\tool\\base_data\\Trading_Day.txt"
G_DOM = xml.dom.minidom.parse(TRADE_PHASE_FILE_NAME)
OUT_FILE_FOLDER = "F:\\IC_Contract_Spread\\picture\\"
LIMIT_TRADE_VOLUME = 10000
LIMIT_TICK_CHANGE = 5
G_TRADE_PHASE_FOLDER = "F:\\tool\\trade_phase\\"
OUTER_DATA_CHANGE_FILE_NAME = 'E:\\quote_data\\outer_data_change\\query_rs.csv'
DATA_CHANGE_COLUMNS = ['Quote_Day', 'Operater_ID', 'Source_Variety_Name', 'Refer_Quote_Time', 'Refer_Quote_Price',
                       'Open_Trade_Time', 'Last_Quote_Price', 'Change_Ratio', 'Influence_Variety_Name', 'Influence_Instrument_ID']

# 方向常量
DIRECTION_BUY = 0               # 买
DIRECTION_SELL = 1              # 卖

# 开平常量
OFFSET_NONE = u'无开平'
OFFSET_OPEN = 0                 # 开仓
OFFSET_CLOSE = 1                # 平仓
OFFSET_CLOSETODAY = 3           # 平今
OFFSET_CLOSEYESTERDAY = 4       # 平昨
