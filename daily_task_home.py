# -*- coding: utf-8 -*-
import time
import xlrd
import os
from send_email_outlook import send_email_outlook

path = os.path.dirname(os.path.realpath(__file__))

#判断报告类型
intraday = time.localtime(time.time())
if intraday.tm_wday == 1:
    report_type = 'w'
elif intraday.tm_mday == 1:
    report_type = 'm'
else:
    report_type = 'd'

#发送邮件
xlwb = xlrd.open_workbook(path + u'\\mail_config_home.xlsx')

to_list = []
ws = xlwb.sheets()[0]
for i in range(1,ws.nrows):
    to_list.append(ws.cell(i,0).value.encode('utf-8'))

att_list = []
if report_type == 'd':
    ws = xlwb.sheets()[1]
elif report_type == 'w':
    ws = xlwb.sheets()[2]
else:
    ws = xlwb.sheets()[3]
for i in range(1,ws.nrows):
    command = 'python '+path+'\\report\\' + ws.cell(i,4).value.encode('utf-8')
    os.system(command)
    att_list.append(path + '\\report\\files\\' + ws.cell(i,3).value.encode('utf-8'))

send_email_outlook(to_list,att_list)
 