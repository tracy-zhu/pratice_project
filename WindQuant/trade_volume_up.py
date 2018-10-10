# -*- coding: utf-8 -*-

from WindPy import *
from datetime import *
import pandas as pd


w.start()
end_Date = w.tdaysoffset(-1,datetime.today() , "").Times[0]
end_Date = end_Date.strftime("%Y%m%d")
start_Date = w.tdaysoffset(-10, end_Date, "").Times[0]
start_Date = start_Date.strftime("%Y%m%d")
code_list = w.wset("sectorconstituent","date="+end_Date+";sectorid=a001010100000000")
volume_average = w.wss(code_list.Data[1],"avg_vol_per","startDate="+start_Date+";endDate="+end_Date+"")
volume = w.wss(code_list.Data[1],"volume","tradeDate="+end_Date+";cycle=D")
result = pd.DataFrame(columns=['股票代码','股票简称','上一个交易日的成交量'])
for i in range(len(code_list.Data[0])):
    if(volume.Data[0][i]> 3*volume_average.Data[0][i]):
        result.loc[len(result)]=[code_list.Data[1][i], code_list.Data[2][i], volume.Data[0][i]]
        i = i + 1
result.to_excel('data/选股结果.xlsx') #保存选股结果到excel
result

from WindPy import *
import pandas as pd
w.start()

trading_day = '2018-07-16'
start_date = '2018-07-09'
limit_pre_pct = 20
limit_bit_pin_ratio = 0.5
list_A = w.wset("SectorConstituent",u"date=20130608;sector=全部A股").Data[1] 

wss_str = 'tradedate={trading_day};cycle=1;priceadj=1;startdate={start_date};enddate={end_date}'.format(trading_day=trading_day, start_date=start_date, end_date=trading_day)
his = w.wss(list_A, "sec_name,open,high,low,close,volume,pct_chg,avg_vol_per,pct_chg_per", wss_str)
# his = w.wss("000001.SZ,600000.SH", "avg_vol_per,avg_amt_per", "startDate=2018-06-15;endDate=2018-07-15")
data = pd.DataFrame(his.Data,columns=his.Codes,index=his.Fields).T
data['volume_up_ratio'] = data["VOLUME"] / data["AVG_VOL_PER"]
data['is_exists'] = (data["HIGH"] - data["LOW"])
data = data[data['is_exists'] != 0]
data['bit_pin_ratio'] = (data["HIGH"] - data["CLOSE"]) / (data["HIGH"] - data["LOW"])
data['day_pct']  = data["CLOSE"] - data["OPEN"]
data = data[data['day_pct'] > 0]
data = data[data['PCT_CHG_PER'] < limit_pre_pct]
data = data[data['bit_pin_ratio'] < limit_bit_pin_ratio]
sort_df = data.sort_values(by='volume_up_ratio', ascending=False)
sort_df.head()