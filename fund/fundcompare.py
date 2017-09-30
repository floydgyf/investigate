# -*- coding: utf-8 -*-
from pandas import Series, DataFrame
import pandas as pd
import numpy as np
import scipy.stats as scs

import pandas.util.testing as tm

from WindPy import *
from datetime import *
from pandas.tseries.offsets import Day,MonthEnd,YearOffset
#from dateutil.parser import parse
w.start()



#------------------------------------------------------------------------------------
import numpy as np
import pandas as pd
import xlrd, xlwt
#import xlsxwriter
import matplotlib.pyplot as plt

path= 'E:\Alice\cc\\'

lgd=['b-','b--','b-.','b:','g-','g--','g-.','g:','r-','r--','r-.','r:','c-','c--','c-.','c:','m-','m--','m-.','m:','y-','y--','y-.','y:',]
#----------------------


sdate="2017-01-01"	#数据起始日
vdate="2017-8-31"	#数据结束日
zone=100	#估算平均数和标准差的区间长度。例如5表示5个交易日

tday=w.tdays(sdate, vdate, "").Data[0]	#交易日

fcl=["450009.OF","163110.OF","160211.OF","163001.OF","000523.OF","530017.OF","000205.OF","000290.OF","519675.OF"]
lgd1=DataFrame(lgd[0:len(fcl)],index=fcl)	#图例

#先从wind导出数据保存
nav=[]
for i in fcl:
	fc=i
	a=w.wsd(fc, "NAV_adj",sdate, vdate, "Fill=Previous;PriceAdj=F").Data[0]	#复权单位净值
	nav.append(a)

navfm=DataFrame(nav)

#-------------

xl=[]
yl=[]
for i in fcl:
	fc=i

	#tday=w.wsd(fc, "NAV_adj", sdate, vdate, "Fill=Previous;PriceAdj=F").Times
	nav=w.wsd(fc, "NAV_adj",sdate, vdate, "Fill=Previous;PriceAdj=F").Data[0]	#复权单位净值

	rnav=[0]	#较前一日单位净值增长率
	for i in range(0,len(nav)-1):
		r=nav[i+1]/nav[i]-1
		rnav.append(r)


	x=hist(rnav)[1][0:10]
	y=hist(rnav)[0]

	xl.append(x)
	yl.append(y)



#-----------------------
#画累积密度函数图更好。

ylacc=[]
for i in range(0,len(fcl)):
	yacc=[]
	for j in range(1,len(yl[0])+1):
		z=yl[i][0:j].sum()
		yacc.append(z)
	ylacc.append(yacc)

ylacc_per=ylacc/yl[0].sum()

for i in range(0,len(fcl)):
	plt.plot(xl[i],ylacc_per[i],lgd[i],label=fcl[i])	#累积密度分布图

plt.legend(loc='lower right')
plt.show()
plt.title('Accmulated Density of 1-day Return')
plt.xlabel('1-day Return')
plt.ylabel('Accmulated Density')
#画分界线
dy=Series(range(0,101))/100
dx=np.zeros((1,len(dy)))[0]
plt.plot(dx,dy,'k')


#或者直接计算收益率<0的个数，除以总数就可以知道多少交易日收益率为正


#----------------------

for i in range(0,len(fcl)):
	plt.plot(xl[i],yl[i],lgd[i],label=fcl[i])	#历史分布图

#---------------------------------

#换一种方法画累积密度图

tday=np.array(range(0,10))
a=random.randn(10)
a.sort()	#从小到大排序

tday_per=tday/float(len(tday))

plt.plot(a,tday_per)








