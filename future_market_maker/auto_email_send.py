# -*- coding: utf-8 -*-
"""

# 用于每天定时给李老师发送数据文件
# 首先要将当天的文件选取出来，然后进行压缩

Tue 2018/5/15

@author: Tracy Zhu
"""
# 导入系统库
from datetime import datetime
import smtplib
import email
from email.mime.text import MIMEText
import mimetypes
import os

sender = "zhuhaoran_swufe@163.com"
receiver = ["243560442@qq.com"]
# receiver = ["2034144879@qq.com"]
mail_host = 'smtp.163.com'

trading_date = datetime.now()
trading_day = trading_date.strftime('%Y%m%d')


#邮件内容设置
msg = MIMEText('content','plain','utf-8')
#邮件主题
msg['Subject'] = 'quote_data_' + trading_day
#发送方信息
msg['From'] = sender
#接受方信息
msg['To'] = receiver[0]

file_name = "E:\\quote_data\\chose_instrument_id\\" + trading_day + ".rar"

data = open(file_name, 'rb')
ctype,encoding = mimetypes.guess_type(file_name)
if ctype is None or encoding is not None:
    ctype = 'application/octet-stream'
maintype,subtype = ctype.split('/', 1)
file_msg = email.MIMEBase.MIMEBase(maintype, subtype)
file_msg.set_payload(data.read())
data.close( )
email.Encoders.encode_base64(file_msg)

basename = os.path.basename(file_name)
file_msg.add_header('Content-Disposition','attachment', filename = basename)#修改邮件头
msg.attach(file_msg)


try:
    smtp = smtplib.SMTP()
    smtp.connect(mail_host, 0)
    smtp.login(sender, "zhr20140705")
    smtp.sendmail(sender, receiver, msg.as_string())
    print('success!')
    smtp.quit()
except smtplib.SMTPException as e:
    print('error', e)

