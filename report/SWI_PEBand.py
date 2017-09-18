# -*- coding: utf-8 -*-
from WindPy import *
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
import time
import os

mpl.rcParams['font.sans-serif']=['Microsoft YaHei'] #用来正常显示中文标签 

tmp = w.start()
import base64
import io

#申万一级行业分析
begindate = "20140101"
enddate = time.strftime("%Y%m%d")

 
windout = w.wset("sectorconstituent","date="+ enddate +";sectorid=a39901011g000000")
seclist = windout.Data[1:3]
 
windout = w.wsd(seclist[0], "close", begindate, enddate, "PriceAdj=F")
datelist = windout.Times
close_data = windout.Data

windout = w.wsd(seclist[0], "pe_ttm", begindate, enddate, "PriceAdj=F")
pe_data = windout.Data

#创建HTML文件
path = os.path.dirname(os.path.realpath(__file__))
print path
f = open(path + "\\files\\SWI_PEBand.html",'w')
html_str = '''<meta http-equiv="content-type" content="text/html; charset=UTF-8" />
<font size="5" face = "Microsoft YaHei"><b> 申万一级行业PE-Band </b></font> 
<br><font face = "Microsoft YaHei">    截止日期：'''+enddate+ '</font><br>'

f.write(html_str)

for i in range(len(seclist[0])):
    #PE分档
    l1 = round(min(pe_data[i]),1)
    l5 = round(max(pe_data[i]),1)
    l2 = round(l1+0.25*(l5-l1),1)
    l3 = round(l1+0.5*(l5-l1),1)
    l4 = round(l1+0.75*(l5-l1),1)
    
    #生成图片
    fig = plt.figure(figsize=(10,5))
    ax1 = plt.subplot()
    #ax2 = ax1.twinx()
    plt.title(seclist[1][i])
    #收益率曲线
    #xSeries = datelist
    #ySeries = (np.array(close_data[i])/close_data[i][0] - 1)*100
    #ax2.plot(xSeries, ySeries, label=seclist[1][i]+u" 收益率")
    
    #价格曲线
    xSeries = datelist
    ySeries = np.array(close_data[i])
    #ax1.plot(xSeries, ySeries, label=seclist[1][i])
    ax1.plot(xSeries, ySeries)
    
    #L5档
    xSeries = datelist
    ySeries = np.array(close_data[i])/np.array(pe_data[i])*l5
    ax1.plot(xSeries, ySeries, "--", label=str(l5)+u"  PE")
    #L4档
    xSeries = datelist
    ySeries = np.array(close_data[i])/np.array(pe_data[i])*l4
    ax1.plot(xSeries, ySeries, "--", label=str(l4)+u"  PE")
    #L3档
    xSeries = datelist
    ySeries = np.array(close_data[i])/np.array(pe_data[i])*l3
    ax1.plot(xSeries, ySeries, "--", label=str(l3)+u"  PE")
    #L2档
    xSeries = datelist
    ySeries = np.array(close_data[i])/np.array(pe_data[i])*l2
    ax1.plot(xSeries, ySeries, "--", label=str(l2)+u"  PE")
    #L1档
    xSeries = datelist
    ySeries = np.array(close_data[i])/np.array(pe_data[i])*l1
    ax1.plot(xSeries, ySeries, "--",label=str(l1)+u"  PE")
    
    #坐标轴格式设置
    plt.xlim((begindate,enddate))
    ax1.xaxis.set_major_formatter(mpl.dates.DateFormatter('%y%m%d'))
    #ax2.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.2f%%'))
    ax1.grid(True)
    ax1.legend(loc='best')
    
    #plt.savefig("D:\\Investigate\\img\\" + seclist[1][i] +".png")
    #base64.b64encode(s)
    #f=open("D:\\Investigate\\img\\" + seclist[1][i] +".png",'rb') #二进制方式打开图文件
    
    canvas = fig.canvas
    buffer = io.BytesIO()
    canvas.print_png(buffer)
    image_data=buffer.getvalue()
    buffer.close()
    base64_data = base64.b64encode(image_data) #读取文件内容，转换为base64编码
    
    html_str = '<br><img src="data:image/png;base64,'+ base64_data + '"></div><br>'
    f.write(html_str)
    plt.close('all')
f.close()

