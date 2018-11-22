## -*- coding: gb2312 -*
from python_base.Python_Data_Type import *
from python_base.Python_Osprey_Field import *
import string

#Read 最优行情 From csv File   
def Get_CBest_Market_Data_Field_From_Line(read_line_txt_):
    field_list = read_line_txt_.split(",")
    read_field = CBest_Market_Data_Field()
    read_field.Instrument_ID = field_list[0] 
    read_field.Update_Time = field_list[1] 
    try:
        read_field.Update_Millisec = string.atoi(field_list[2])
    except  ValueError :
        read_field.Update_Millisec = 0			
    read_field.Trading_Day = field_list[3] 
    try:
        read_field.Pre_Settlement_Price = string.atof(field_list[4])
    except  ValueError :
        read_field.Pre_Settlement_Price = 0.0
    try:
        read_field.Pre_Close_Price = string.atof(field_list[5])
    except  ValueError :
        read_field.Pre_Close_Price = 0.0
    try:
        read_field.Pre_Open_Interest = string.atof(field_list[6])
    except  ValueError :
        read_field.Pre_Open_Interest = 0.0
    try:
        read_field.Pre_Delta = string.atof(field_list[7])
    except  ValueError :
        read_field.Pre_Delta = 0.0
    try:
        read_field.Open_Price = string.atof(field_list[8])
    except  ValueError :
        read_field.Open_Price = 0.0
    try:
        read_field.Highest_Price = string.atof(field_list[9])
    except  ValueError :
        read_field.Highest_Price = 0.0
    try:
        read_field.Lowest_Price = string.atof(field_list[10])
    except  ValueError :
        read_field.Lowest_Price = 0.0
    try:
        read_field.Close_Price = string.atof(field_list[11])
    except  ValueError :
        read_field.Close_Price = 0.0
    try:
        read_field.Upper_Limit_Price = string.atof(field_list[12])
    except  ValueError :
        read_field.Upper_Limit_Price = 0.0
    try:
        read_field.Lower_Limit_Price = string.atof(field_list[13])
    except  ValueError :
        read_field.Lower_Limit_Price = 0.0
    try:
        read_field.Settlement_Price = string.atof(field_list[14])
    except  ValueError :
        read_field.Settlement_Price = 0.0
    try:
        read_field.Curr_Delta = string.atof(field_list[15])
    except  ValueError :
        read_field.Curr_Delta = 0.0
    try:
        read_field.Life_Hight = string.atof(field_list[16])
    except  ValueError :
        read_field.Life_Hight = 0.0
    try:
        read_field.Life_Low = string.atof(field_list[17])
    except  ValueError :
        read_field.Life_Low = 0.0
    try:
        read_field.Last_Price = string.atof(field_list[18])
    except  ValueError :
        read_field.Last_Price = 0.0
    try:
        read_field.Last_Match_Volume = string.atoi(field_list[19])
    except  ValueError :
        read_field.Last_Match_Volume = 0			
    try:
        read_field.Turnover = string.atof(field_list[20])
    except  ValueError :
        read_field.Turnover = 0.0
    try:
        read_field.Total_Match_Volume = string.atoi(field_list[21])
    except  ValueError :
        read_field.Total_Match_Volume = 0			
    try:
        read_field.Open_Interest = string.atof(field_list[22])
    except  ValueError :
        read_field.Open_Interest = 0.0
    try:
        read_field.Interest_Change = string.atoi(field_list[23])
    except  ValueError :
        read_field.Interest_Change = 0			
    try:
        read_field.Average_Price = string.atof(field_list[24])
    except  ValueError :
        read_field.Average_Price = 0.0
    try:
        read_field.Bid_Price1 = string.atof(field_list[25])
    except  ValueError :
        read_field.Bid_Price1 = 0.0
    try:
        read_field.Bid_Volume1 = string.atoi(field_list[26])
    except  ValueError :
        read_field.Bid_Volume1 = 0			
    try:
        read_field.Ask_Price1 = string.atof(field_list[27])
    except  ValueError :
        read_field.Ask_Price1 = 0.0
    try:
        read_field.Ask_Volume1 = string.atoi(field_list[28])
    except  ValueError :
        read_field.Ask_Volume1 = 0			
    read_field.Exchange_ID = field_list[29] 
    return read_field


#Read 最优行情 From csv File   
def Get_Change_CBest_Market_Data_Field_From_Line(read_line_txt_,out_best_market_field):
    field_list = read_line_txt_.split(",")
    out_best_market_field.Update_Time = field_list[1] 
    try:
        out_best_market_field.Update_Millisec = string.atoi(field_list[2])
    except  ValueError :
        out_best_market_field.Update_Millisec = 0			
    try:
        out_best_market_field.Highest_Price = string.atof(field_list[9])
    except  ValueError :
        out_best_market_field.Highest_Price = 0.0
    try:
        out_best_market_field.Lowest_Price = string.atof(field_list[10])
    except  ValueError :
        out_best_market_field.Lowest_Price = 0.0
    try:
        out_best_market_field.Close_Price = string.atof(field_list[11])
    except  ValueError :
        out_best_market_field.Close_Price = 0.0
    try:
        out_best_market_field.Curr_Delta = string.atof(field_list[15])
    except  ValueError :
        out_best_market_field.Curr_Delta = 0.0
    try:
        out_best_market_field.Last_Price = string.atof(field_list[18])
    except  ValueError :
        out_best_market_field.Last_Price = 0.0
    try:
        out_best_market_field.Last_Match_Volume = string.atoi(field_list[19])
    except  ValueError :
        out_best_market_field.Last_Match_Volume = 0			
    try:
        out_best_market_field.Turnover = string.atof(field_list[20])
    except  ValueError :
        out_best_market_field.Turnover = 0.0
    try:
        out_best_market_field.Total_Match_Volume = string.atoi(field_list[21])
    except  ValueError :
        out_best_market_field.Total_Match_Volume = 0			
    try:
        out_best_market_field.Open_Interest = string.atof(field_list[22])
    except  ValueError :
        out_best_market_field.Open_Interest = 0.0
    try:
        out_best_market_field.Interest_Change = string.atoi(field_list[23])
    except  ValueError :
        out_best_market_field.Interest_Change = 0			
    try:
        out_best_market_field.Bid_Price1 = string.atof(field_list[25])
    except  ValueError :
        out_best_market_field.Bid_Price1 = 0.0
    try:
        out_best_market_field.Bid_Volume1 = string.atoi(field_list[26])
    except  ValueError :
        out_best_market_field.Bid_Volume1 = 0			
    try:
        out_best_market_field.Ask_Price1 = string.atof(field_list[27])
    except  ValueError :
        out_best_market_field.Ask_Price1 = 0.0
    try:
        out_best_market_field.Ask_Volume1 = string.atoi(field_list[28])
    except  ValueError :
        out_best_market_field.Ask_Volume1 = 0			
    return out_best_market_field

def Get_String_From_CBest_Market_Data_Field(read_field):
    ret_string=""
    ret_string= read_field.Instrument_ID 
    ret_string= ret_string + "," + str(read_field.Update_Time)
    ret_string= ret_string + "," + str(read_field.Update_Millisec)		
    ret_string= ret_string + "," + read_field.Trading_Day
    ret_string= ret_string + "," + str(read_field.Pre_Settlement_Price)

    ret_string= ret_string + "," + str(read_field.Pre_Close_Price)

    ret_string= ret_string + "," + str(read_field.Pre_Open_Interest)

    ret_string= ret_string + "," + str(read_field.Pre_Delta)

    ret_string= ret_string + "," + str(read_field.Open_Price)

    ret_string= ret_string + "," + str(read_field.Highest_Price)

    ret_string= ret_string + "," + str(read_field.Lowest_Price)

    ret_string= ret_string + "," + str(read_field.Close_Price)

    ret_string= ret_string + "," + str(read_field.Upper_Limit_Price)

    ret_string= ret_string + "," + str(read_field.Lower_Limit_Price)

    ret_string= ret_string + "," + str(read_field.Settlement_Price)

    ret_string= ret_string + "," + str(read_field.Curr_Delta)

    ret_string= ret_string + "," + str(read_field.Life_Hight)

    ret_string= ret_string + "," + str(read_field.Life_Low)

    ret_string= ret_string + "," + str(read_field.Last_Price)

    ret_string= ret_string + "," + str(read_field.Last_Match_Volume)	

    ret_string= ret_string + "," + str(read_field.Turnover)

    ret_string= ret_string + "," + str(read_field.Total_Match_Volume)		

    ret_string= ret_string + "," + str(read_field.Open_Interest)

    ret_string= ret_string + "," + str(read_field.Interest_Change)		

    ret_string= ret_string + "," + str(read_field.Average_Price)

    ret_string= ret_string + "," + str(read_field.Bid_Price1)

    ret_string= ret_string + "," + str(read_field.Bid_Volume1)		

    ret_string= ret_string + "," + str(read_field.Ask_Price1)

    ret_string= ret_string + "," + str(read_field.Ask_Volume1)
                                       
    ret_string= ret_string + "," + read_field.Exchange_ID
    return ret_string
