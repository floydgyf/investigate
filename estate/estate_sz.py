# -*- coding: utf-8 -*-
from WindPy import *
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
import time

def draw_to_html(title,df,format,f):
    import base64
    import io
    
    mpl.rcParams['font.sans-serif']=['Microsoft YaHei'] #用来正常显示中文标签 
    
    fig = plt.figure(figsize=(10,5))
    ax1 = plt.subplot()
    #ax2 = ax1.twinx()
    plt.title(title)
    xSeries = df.index
    
    for i in df.columns:
        ySeries = df[i]
        ax1.plot(xSeries, ySeries, label = i)
        
    #坐标轴格式设置
    if format[0] <> '':
        ax1.xaxis.set_major_formatter(mpl.dates.DateFormatter(format[0]))
    if format[1] <> '':
        ax1.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter(format[1]))
        
    #ax2.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.2f%%'))
    ax1.grid(True)
    ax1.legend(loc='best')
    
    canvas = fig.canvas
    buffer = io.BytesIO()
    canvas.print_png(buffer)
    image_data=buffer.getvalue()
    buffer.close()
    base64_data = base64.b64encode(image_data) #读取文件内容，转换为base64编码
        
    html_str = '<br><img src="data:image/png;base64,'+ base64_data + '"></div><br>'
    #f.write(html_str)
    #plt.close('all')
    




tmp = w.start()




#申万一级行业分析
begindate = "20000101"
enddate = time.strftime("%Y%m%d")

#创建HTML文件
f = open("files\\estate.html",'w')
html_str = '''<meta http-equiv="content-type" content="text/html; charset=UTF-8" />
<font size="5" face = "Microsoft YaHei"><b> 深圳房地产价格分析</b></font> 
<br><font face = "Microsoft YaHei">    截止日期：'''+enddate+ '</font><br>'
f.write(html_str)



#全国

windout = w.edb("S2707408,S2707409,S2707410", begindate, enddate,"Fill=Previous")
#S2707408 70个大中城市新建住宅价格指数:一线城市:环比
#S2707409 70个大中城市新建住宅价格指数:二线城市:环比
#S2707410 70个大中城市新建住宅价格指数:三线城市:环比
index = [u'一线城市:环比',u'二线城市:环比',u'三线城市:环比']
df = pd.DataFrame(windout.Data, columns = windout.Times, index = index).T
format = ['%y%m%d','%.2f%%','']
draw_to_html(u"70个大中城市新建住宅价格指数:环比",df,format,f)

#房地产贷款余额同比变化
windout = w.edb("S0000017,S0000019,S0000021", begindate, enddate)
#S0000017 商业性房地产贷款余额同比增长
#S0000019 房地产开发贷款余额:同比增长
#S0000021 个人住房贷款余额:同比增长

index = [u'商业性房地产贷款余额同比增长',u'房地产开发贷款余额:同比增长',u'个人住房贷款余额:同比增长']
df = pd.DataFrame(windout.Data, columns = windout.Times, index = index).T
format = ['%y%m%d','%.2f%%','']
draw_to_html(u"房地产贷款余额同比变化",df,format,f)

#深圳：中原领先指数
windout = w.edb("S0109845,S0109846,S0109847,S0109848,S0109849,S0109850,S0109851,S0178596", begindate, enddate)
#S0109852 深圳：中原领先指数:全市
#S0109853 深圳：中原领先指数:福田
#S0109854 深圳：中原领先指数:罗湖
#S0109855 深圳：中原领先指数:南山
#S0109856 深圳：中原领先指数:盐田
#S0109857 深圳：中原领先指数:宝安
#S0109858 深圳：中原领先指数:龙岗
#S0178597 深圳：中原领先指数:龙华
index = [u'全市',u'福田',u'罗湖',u'南山',u'盐田',u'宝安',u'龙岗',u'龙华']
df = pd.DataFrame(windout.Data, columns = windout.Times, index = index).T
format = ['%y%m%d','','']
draw_to_html(u"深圳：中原领先指数",df,format,f)

#深圳商品房成交数据
windout = w.edb("S0168110,S0168114,S0168118", begindate, enddate,"Fill=Previous")
#S0168110 深圳:商品房成交套数:住宅
#S0168114 深圳:商品房成交面积:住宅
#S0168118 深圳:商品房成交均价:住宅
index = [u'成交套数',u'成交面积',u'成交均价']
df = pd.DataFrame(windout.Data, columns = windout.Times, index = index).T
format = ['%y%m%d','%.2f%%','']
draw_to_html(u"深圳:商品房成交",df,format,f)

#深圳：商品房价格
windout = w.edb("S0106723,S0106724,S0106725,S0106726,S0106727,S0106728", begindate, enddate)
#S0109852 深圳:商品房成交均价:宝安
#S0109853 深圳:商品房成交均价:福田
#S0109854 深圳:商品房成交均价:龙岗
#S0109855 深圳:商品房成交均价:罗湖
#S0109856 深圳:商品房成交均价:南山
#S0109857 深圳:商品房成交均价:盐田
index = [u'宝安',u'福田',u'龙岗',u'罗湖',u'南山',u'盐田']
df = pd.DataFrame(windout.Data, columns = windout.Times, index = index).T
#30天移动平均
for i in range(len(df.columns)):
    tmp = list(df[df.columns[i]])
    s = 0
    count = 0
    for j in range(len(tmp)):
        if not np.isnan(tmp[j]):
            s += tmp[j]
            count += 1
        if j >= 30 and (not np.isnan(tmp[j-30])):
            s -= tmp[j-30]
            count-=1
        if count >= 1:
            df[df.columns[i]][j] = s/count
format = ['%y%m%d','','']
draw_to_html(u"深圳：商品房价格",df,format,f)



#深圳二手房成交均价
windout = w.edb("S0109852,S0109853,S0109854,S0109855,S0109856,S0109857,S0109858,S0178597", begindate, enddate)
#S0109852 深圳二手房成交均价:全市
#S0109853 深圳二手房成交均价:福田
#S0109854 深圳二手房成交均价:罗湖
#S0109855 深圳二手房成交均价:南山
#S0109856 深圳二手房成交均价:盐田
#S0109857 深圳二手房成交均价:宝安
#S0109858 深圳二手房成交均价:龙岗
#S0178597 深圳二手房成交均价:龙华

index = [u'全市',u'福田',u'罗湖',u'南山',u'盐田',u'宝安',u'龙岗',u'龙华']
df = pd.DataFrame(windout.Data, columns = windout.Times, index = index).T
format = ['%y%m%d','','']
draw_to_html(u"深圳二手房成交均价",df,format,f)

#福田：二手房成交均价
windout = w.edb("S0109859,S0109860,S0109861,S0109862,S0109863,S0109864,S0109865,S0109866,S0109867,S0109868", begindate, enddate)
#S0109859 深圳:二手房成交均价:福田区:八卦路板块
#S0109860 深圳:二手房成交均价:福田区:白沙岭板块
#S0109861 深圳:二手房成交均价:福田区:保税板块
#S0109862 深圳:二手房成交均价:福田区:皇岗板块
#S0109863 深圳:二手房成交均价:福田区:景田--香蜜湖板块
#S0109864 深圳:二手房成交均价:福田区:莲花板块（含中心北区）
#S0109865 深圳:二手房成交均价:福田区:梅林板块
#S0109866 深圳:二手房成交均价:福田区:农科中心--竹子林板块
#S0109867 深圳:二手房成交均价:福田区:新洲--上下沙板块
#S0109868 深圳:二手房成交均价:福田区:中心南区

index = [u'八卦路板块',u'白沙岭板块',u'保税板块',u'皇岗板块',u'景田--香蜜湖板块',u'莲花板块（含中心北区）',u'梅林板块',u'农科中心--竹子林板块',u'新洲--上下沙板块',u'中心南区']
df = pd.DataFrame(windout.Data, columns = windout.Times, index = index).T
format = ['%y%m%d','','']
draw_to_html(u"福田区：二手房成交均价",df,format,f)


f.close()

