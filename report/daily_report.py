# -*- coding: utf-8 -*-
from WindPy import *
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
import time
import os
import base64
import io

#创建HTML文件
path = os.path.dirname(os.path.realpath(__file__))
f = open(path + "\\files\\SWI_PEBand.html",'w')
html_str = '''<meta http-equiv="content-type" content="text/html; charset=UTF-8" />
<font size="5" face = "Microsoft YaHei"><b> 申万一级行业PE-Band </b></font> 
<br><font face = "Microsoft YaHei">    截止日期：'''+enddate+ '</font><br>'

f.write(html_str)

mpl.rcParams['font.sans-serif']=['Microsoft YaHei'] #用来正常显示中文标签 

w.start()

intraday = time.strftime("%Y%m%d")

################权益市场

#主要指数近期收益率：当日、近5交易日、近21个交易日
sec_list = ['000001.SH','399001.SZ','399005.SZ','399006.SZ','HSI.HI','000903.SH','000300.SH','000905.SH','000852.SH']
index = w.wss(sec_list, "sec_name").Data[0]

fig = plt.figure(figsize=(6,8),dpi=100)
ax1 = plt.subplot()
#ax2 = ax1.twinx()
plt.title(u'主要指数收益率')

begindate = intraday
xSeries = range(0,len(sec_list)*4,4)[::-1]
ySeries = w.wss(sec_list, "pct_chg_per","startDate=" + begindate + ";endDate=" + intraday).Data[0]
ax1.barh(xSeries, ySeries, label = u'今日收益率')

begindate = w.tdaysoffset(-5, intraday, "").Data[0][0].strftime("%Y%m%d")
xSeries = range(1,len(sec_list)*4,4)[::-1]
ySeries = w.wss(sec_list, "pct_chg_per","startDate=" + begindate + ";endDate=" + intraday).Data[0]
ax1.barh(xSeries, ySeries, label = u'近5日收益率')

begindate = w.tdaysoffset(-21, intraday, "").Data[0][0].strftime("%Y%m%d")
xSeries = range(2,len(sec_list)*4,4)[::-1]
ySeries = w.wss(sec_list, "pct_chg_per","startDate=" + begindate + ";endDate=" + intraday).Data[0]
ax1.barh(xSeries, ySeries, label = u'近1月收益率')

ax1.xaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.2f%%'))
plt.yticks(np.array(xSeries) - 1 ,index) 

ax1.grid(axis='x')
ax1.legend(loc='upper right')



#固收市场

#固定收益利率分析

begindate = "20170101"
enddate = "20170814"

seclist = ['M1000158','M1000166','M1004298','M1004306','M1004263','M1004271','M1000394','M1000398','M1001794','M1001795']
windout = w.edb(seclist, begindate, enddate, "Fill=Previous")
#M1000158 中债国债到期1年
#M1000166 中债国债到期10年
#M1004298 中债地方政府债到期（AAA）1年
#M1004306 中债地方政府债到期（AAA）10年
#M1004263 中债国开债到期收益率1年
#M1004271 中债国开债到期收益率10年
#M1000394 中债企业债到期收益率（AA+）1年
#M1000398 中债企业债到期收益率（AA+）5年
#M1001794 R001
#M1001795 R007

datelist = windout.Times
data = windout.Data
df = pd.DataFrame(data, columns = datelist, index =windout.Codes).T



#国债到期收益率曲线分析
plt.figure(figsize=(10,5))
plt.title(u'国债到期收益率曲线分析')
ax1 = plt.subplot()

#M1000158 中债国债到期1年
xSeries = datelist
ySeries = df["M1000158"]
ax1.plot(xSeries, ySeries, label = u'中债国债到期收益率1年')
#M1000166 中债国债到期10年
xSeries = datelist
ySeries = df["M1000166"]
ax1.plot(xSeries, ySeries, label = u'中债国债到期收益率10年')

#坐标轴格式设置
ax1.xaxis.set_major_formatter(mpl.dates.DateFormatter('%y%m%d'))
ax1.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.2f%%'))
ax1.grid(True)
ax1.legend(loc='upper left')

'''for i in range(len(seclist[0])):
    plt.figure(figsize=(10,5))
    ax = plt.subplot()
    plt.title(seclist[1][i])
    ySeries = np.array(data[i])/data[i][0] - 1
    plt.plot(datelist, ySeries, label=seclist[1][i])
    ax.xaxis.set_major_formatter(DateFormatter('%y%m%d'))
    ax.grid(True)
    #plt.legend(loc='upper left')
'''
plt.show()

#利率债到期收益率曲线分析
fig = plt.figure(figsize=(10,5))
ax1 = plt.subplot()
ax2 = ax1.twinx()
ax1.set_title(u'利率债到期收益率曲线分析',fontsize = 14)

#M1000166 中债国债到期10年
xSeries = datelist
ySeries = df["M1000166"]
l1 = ax1.plot(xSeries, ySeries, label = u'中债国债到期收益率10年')
#M1004306 中债地方政府债到期（AAA）10年
xSeries = datelist
ySeries = df["M1004306"]
l2 = ax1.plot(xSeries, ySeries, label = u'中债地方政府债到期（AAA）10年')
#M1004271 中债国开债到期收益率10年
xSeries = datelist
ySeries = df["M1004271"]
l3 = ax1.plot(xSeries, ySeries, label = u'中债国开债到期收益率10年')

#中债国开债到期收益率10年 利差
xSeries = datelist
ySeries = df["M1004271"]-df["M1000166"]
l4 = ax2.fill_between(xSeries, ySeries, facecolor='green', alpha = 0.2, label = u'国开债10年 利差')
#中债地方政府债（AAA）到期收益率10年 利差
xSeries = datelist
ySeries = df["M1004306"]-df["M1000166"]
l5 = ax2.fill_between(xSeries, ySeries, facecolor='b', alpha = 0.2, label = u'地方政府债10年 利差')


#坐标轴格式设置
ax1.xaxis.set_major_formatter(mpl.dates.DateFormatter('%y%m%d'))
ax1.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.2f%%'))
ax2.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.2f%%'))
ax2.set_ylim([0.3,1])
ax1.grid(True)
plt.legend(loc = 'best')
#ax2.legend(loc='upper')


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

