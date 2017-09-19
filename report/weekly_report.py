# -*- coding: utf-8 -*-
from WindPy import *
import numpy as np
import pandas as pd
import time
import os
from print_chart import *


intraday = time.strftime("%Y%m%d")

#创建HTML文件
path = os.path.dirname(os.path.realpath(__file__))
f = open(path + "\\files\\Daily_Report.html",'w')
html_str = '''<meta http-equiv="content-type" content="text/html; charset=UTF-8" />
<font size="5" face = "Microsoft YaHei"><b> 市场行情日报 </b></font> 
<br><font face = "Microsoft YaHei">    截止日期：''' + intraday + '</font><br>'
f.write(html_str)


w.start()
################权益市场

#主要指数近期收益率：当日、近5交易日、近21个交易日
sec_list = ['000001.SH','399001.SZ','399005.SZ','399006.SZ','HSI.HI','000903.SH','000300.SH','000905.SH','000852.SH']
index = w.wss(sec_list, "sec_name").Data[0]
columns = [u'今日收益率',u'近5日收益率',u'近1月收益率']

data=[]
begindate = intraday
data.append(w.wss(sec_list, "pct_chg_per","startDate=" + begindate + ";endDate=" + intraday).Data[0])

begindate = w.tdaysoffset(-5, intraday, "").Data[0][0].strftime("%Y%m%d")
data.append(w.wss(sec_list, "pct_chg_per","startDate=" + begindate + ";endDate=" + intraday).Data[0])

begindate = w.tdaysoffset(-21, intraday, "").Data[0][0].strftime("%Y%m%d")
data.append(w.wss(sec_list, "pct_chg_per","startDate=" + begindate + ";endDate=" + intraday).Data[0])

df = pd.DataFrame(data, columns = index, index =columns).T

draw_barh(df,u'主要指数收益率',f)

#申万行业收益率
sec_list = w.wset("sectorconstituent","date="+ intraday +";sectorid=a39901011g000000").Data[1]
index = w.wss(sec_list, "sec_name").Data[0]
for i in range(len(index)):
    index[i] = index[i].split("(")[0]
columns = [u'今日收益率',u'近5日收益率',u'近1月收益率']

data=[]
begindate = intraday
data.append(w.wss(sec_list, "pct_chg_per","startDate=" + begindate + ";endDate=" + intraday).Data[0])

begindate = w.tdaysoffset(-5, intraday, "").Data[0][0].strftime("%Y%m%d")
data.append(w.wss(sec_list, "pct_chg_per","startDate=" + begindate + ";endDate=" + intraday).Data[0])

begindate = w.tdaysoffset(-21, intraday, "").Data[0][0].strftime("%Y%m%d")
data.append(w.wss(sec_list, "pct_chg_per","startDate=" + begindate + ";endDate=" + intraday).Data[0])

df = pd.DataFrame(data, columns = index, index =columns).T

draw_barh(df,u'申万行业收益率',f)


###########################固收市场#############################################

#国债利率曲线变动
sec_list = ['M1000155','M1000156','M1000158','M1000159','M1000160','M1000162','M1000164','M1000166','M1000167','M1000168','M1000169']
#关键点利率 0.25,0.5,1,2,3,5,7,10,15,20,30
index = ['0.25Y','0.5Y','1Y','2Y','3Y','5Y','7Y','10Y','15Y','20Y','30Y']
begindate = w.tdaysoffset(-21, intraday, "").Data[0][0].strftime("%Y%m%d")
windout = w.edb(sec_list, begindate, intraday)
df = pd.DataFrame(windout.Data, columns = windout.Times, index =index)
df = df[[df.columns[-1],df.columns[-2],df.columns[-5]]]

#图表绘制
interest_curve(u'中债国债收益率曲线变动',df,f)


#国开债利率曲线变动
sec_list = ['M1004260','M1004261','M1004263','M1004264','M1004265','M1004267','M1004269','M1004271','M1004272','M1004273','M1004274']
#关键点利率 0.25,0.5,1,2,3,5,7,10,15,20,30
index = ['0.25Y','0.5Y','1Y','2Y','3Y','5Y','7Y','10Y','15Y','20Y','30Y']
begindate = w.tdaysoffset(-21, intraday, "").Data[0][0].strftime("%Y%m%d")
windout = w.edb(sec_list, begindate, intraday)
df = pd.DataFrame(windout.Data, columns = windout.Times, index =index)
df = df[[df.columns[-1],df.columns[-2],df.columns[-5]]]

#图表绘制
interest_curve(u'中债国开债收益率曲线变动',df,f)



#信用债利率曲线变动
sec_list = ['M1004554','M1000393','M1000394','M1000395','M1000396','M1000398','M1000400','M1000402','M1000403','M1000404','M1000405']
#关键点利率 0.25,0.5,1,2,3,5,7,10,15,20,30
index = ['0.25Y','0.5Y','1Y','2Y','3Y','5Y','7Y','10Y','15Y','20Y','30Y']
begindate = w.tdaysoffset(-21, intraday, "").Data[0][0].strftime("%Y%m%d")
windout = w.edb(sec_list, begindate, intraday)
df = pd.DataFrame(windout.Data, columns = windout.Times, index =index)
df = df[[df.columns[-1],df.columns[-2],df.columns[-5]]]

#图表绘制
interest_curve(u'中债企业债（AA+）收益率曲线变动',df,f)


f.close()

'''
sec_list = ['M1000158','M1000166','M1004298','M1004306','M1004263','M1004271','M1000394','M1000398','M1001794','M1001795']
#windout = w.edb(sec_list, begindate, enddate, "Fill=Previous")
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
'''






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



'''


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
    
'''