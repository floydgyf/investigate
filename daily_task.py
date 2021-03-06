# -*- coding: utf-8 -*-
import time
import xlrd
import os
import socket

path = os.path.dirname(os.path.realpath(__file__))

hostname = socket.gethostname()
if hostname == "SZE7270-1715":
    xlwb = xlrd.open_workbook(path + u'\\task_office.xlsx')
else:
    xlwb = xlrd.open_workbook(path + u'\\task_config.xlsx')

#执行日常任务
intraday = time.localtime(time.time())
if intraday.tm_wday == 0:
    ws = xlwb.sheets()[1]  #周度任务
elif intraday.tm_mday == 1:
    ws = xlwb.sheets()[2]  #月度任务
else:
    ws = xlwb.sheets()[0]  #日度任务
for i in range(1,ws.nrows):
    command = 'python ' + path + ws.cell(i,1).value.encode('utf-8') + ws.cell(i,0).value.encode('utf-8')
    os.system(command)