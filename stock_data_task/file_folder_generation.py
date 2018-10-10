# -*- coding: utf-8 -*-
"""

# 每天生成晨会需要的文件夹

Thu 2018/07/11

@author: Tracy Zhu
"""

# 导入系统库
import sys, os
from datetime import datetime

# 导入用户库
sys.path.append("..")

out_file_folder = u'C:\\Users\\Tracy Zhu\\AppData\\Roaming\\Microsoft\\Windows\\Network Shortcuts\\晨会\\'

now = datetime.now()
end_date = now.strftime('%Y-%m-%d')

file_folder = out_file_folder + end_date
isExists = os.path.exists(file_folder)
if not isExists:
    os.makedirs(file_folder)