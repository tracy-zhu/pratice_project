## -*- coding: gb2312 -*
import os,re
##floder_path  存储行情文件的根目录
##instrument_id  合约名称 
##返回所有该合约的文件名，带路径，且按时间排序
def Get_All_File_By_InstrumentID(floder_path,instrument_id):
    file_list = []
    if floder_path is None:
        raise Exception("floder_path is None")
    for dirpath, dirnames, filenames in os.walk(floder_path):
        for name in filenames:
             #print name
             if name.find(instrument_id) >= 0:
                 file_list.append(dirpath + '\\' + name)
    file_list.sort()           
    return file_list

##floder_path  存储行情文件的根目录
##instrument_id  合约名称 
##返回所有该合约的文件名，带路径，且按时间排序
def Get_All_File_By_InstrumentID_And_Date(floder_path,instrument_id,_begin_date,_end_date):
    if len(_begin_date) < 1:
        return Get_All_File_By_InstrumentID(floder_path,instrument_id)

    file_list = []
    if floder_path is None:
        raise Exception("floder_path is None")
    for dirpath, dirnames, filenames in os.walk(floder_path):
        path_list = os.path.split(dirpath)
        if path_list[-1]>= _begin_date and path_list[-1]<= _end_date:
            for name in filenames:
                if name.find(instrument_id) >= 0:
                    file_list.append(dirpath + '\\' + name)
    file_list.sort()           
    return file_list

'''  example
find_list = Get_All_File_By_InstrumentID("E:\\Quote_Root","IF1409")
for one_file in find_list:
     print one_file
'''

########################  Get_Tick_Quote_Folder_List  #######################
##floder_path  存储行情文件的根目录
##instrument_id  合约名称，如果时间为空，则返回整个 tick quote 根目录下的目录
##返回所有该合约的目录路径，且按时间排序
def Get_Tick_Quote_Folder_List(root_floder_path,instrument_id):
    folder_list = []
    if root_floder_path is None:
        raise Exception("floder_path is None")
    if len(instrument_id) < 1:
        pattern=re.compile(r"\d{8}")
        for dirpath, dirnames, filenames in os.walk(root_floder_path):
            path_list = os.path.split(dirpath)
            if pattern.match(path_list[-1]):
                folder_list.append(dirpath)
    else:
        for dirpath, dirnames, filenames in os.walk(root_floder_path):
            for name in filenames:
                if name.find(instrument_id) >= 0:
                    folder_list.append(dirpath)
    folder_list.sort()           
    return folder_list

########################  get_tick_quote_folder_list  #########################
##floder_path     存储行情文件的根目录
##_instrument_id  文件名,如果为""，则是所有目录
##_begin_date     开始日期
##_end_date       结束时间
##返回所有该合约的目录路径，且按时间排序
def Get_Tick_Quote_Folder_List_By_Instrment_And_Time(root_floder_path,_instrument_id,_begin_date,_end_date):
    result_folder_list=[]
    folder_list = Get_Tick_Quote_Folder_List(root_floder_path,_instrument_id)
    if len(_begin_date) > 1:
        for folder in folder_list:
            path_list = os.path.split(folder)
            if path_list[-1]>= _begin_date and path_list[-1]<= _end_date:
                result_folder_list.append(folder)
    else:
        result_folder_list = folder_list
    return result_folder_list

########################  get_tick_quote_folder_list  #########################
##floder_path  存储行情文件的根目录
##_begin_date  开始日期
##_end_date    结束时间
##返回所有该合约的目录路径，且按时间排序
def Get_Tick_Quote_Folder_List_By_Time(root_floder_path,_begin_date,_end_date):
    return Get_Tick_Quote_Folder_List_By_Instrment_And_Time(root_floder_path,"",_begin_date,_end_date)

########################  get_trade_day  #########################
##floder_path  存储行情文件的根目录
##_begin_date  开始日期
##_end_date    结束时间
##返回交易日，且按时间排序
def Get_Trade_Day_List_By_Time(root_floder_path,_begin_date,_end_date):
    result_trade_day_list=[]
    pattern=re.compile(r"\d{8}")
    check_begin_time = False
    if len(_begin_date)> 2:
    	check_begin_time = True
    
    check_end_time = False
    if len(_end_date) > 2:
    	check_end_time = True

    for dirpath, dirnames, filenames in os.walk(root_floder_path):
        path_list = os.path.split(dirpath)
        if pattern.match(path_list[-1]):
        	if check_begin_time:
        		if path_list[-1] >= _begin_date:
        			if check_end_time:
		        		if path_list[-1] <= _begin_date:
        					result_trade_day_list.append(path_list[-1])
        			else:
        				result_trade_day_list.append(path_list[-1])
        	elif check_end_time:
        		if path_list[-1] <= _begin_date:
        			result_trade_day_list.append(path_list[-1])
        	else:
        		result_trade_day_list.append(path_list[-1])
          
    result_trade_day_list.sort()           
    return result_trade_day_list

