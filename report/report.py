# -*- coding: utf-8 -*-
from WindPy import *
import numpy as np
import pandas as pd
import time
import xlrd
import os
from print_chart import *

    
def avg30(l):
    #30天移动平均
    tmp = list(l)
    s = 0.0
    count = 0
    for i in range(len(tmp)):
        if not np.isnan(tmp[i]):
            s += tmp[i]
            count += 1
        if i >= 30 and (not np.isnan(tmp[i-30])):
            s -= tmp[i-30]
            count-=1
        if count >= 1:
            l[i] = s/count
    return l

def yoy(l):
    tmp = list(l)
    for i in range(len(tmp)):
        if i < 12:
            l[i] = np.nan
        elif not np.isnan(tmp[i]) and not (np.isnan(tmp[i-12]) or tmp[i-12] <= 0):
            l[i] = (float(tmp[i])/float(tmp[i-12])-1)*100
        else:
            l[i] = np.nan
    return l


def trans(l, trans_type):
    if trans_type == "avg30":
        return avg30(l)
    elif trans_type == "YoY":
        return yoy(l)
    

tmp = w.start()

begindate = "20000101"
enddate = time.strftime("%Y%m%d")

path = os.path.dirname(os.path.realpath(__file__))
xlwb = xlrd.open_workbook(path + '\\report_config.xlsx')

for ws in xlwb.sheets():
    #创建HTML文件
    filename  = ws.cell(0,1).value
    f = open(path + "\\files\\" + filename,'w')
    html_str = ws.cell(1,1).value.encode('utf-8')+ '<br><font face = "Microsoft YaHei">    截止日期：' + enddate + '</font><br>'
    f.write(html_str)

    for i in range(10,ws.nrows):
        #初始化新图表
        if ws.cell(i,1).value <> "":
            title = ws.cell(i,1).value
            code_list = []
            index_list = []
            transfer_list = []
        #获取指标列表及相关参数
        elif ws.cell(i,3).value <> "":
            code_list.append(ws.cell(i,3).value)
            index_list.append(ws.cell(i,5).value)
            transfer_list.append(ws.cell(i,6).value)
        #指标处理
        elif ws.cell(i,6).value == u"结束":
            windout = w.edb(code_list, begindate, enddate)
            df = pd.DataFrame(windout.Data, columns = windout.Times, index = index_list).T
            for j in range(len(transfer_list)):
                if transfer_list[j] <> "":
                    df[df.columns[j]] = trans(list(df[df.columns[j]]),transfer_list[j])
            format = [ws.cell(i,7).value, ws.cell(i,8).value, ws.cell(i,9).value]
            draw_plot(title, df, format, f)
        elif ws.cell(i,6).value == u"注释":
            html_str = '<font face = "Microsoft YaHei" size = "2"> &emsp;&emsp;&emsp; *注释：' + ws.cell(i,7).value.encode('utf-8')+ '</font><br>'
            f.write(html_str)
f.close()

