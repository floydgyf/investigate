# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd

def img2html(fig, f):
    import io
    import base64
    
    canvas = fig.canvas
    buffer = io.BytesIO()
    canvas.print_png(buffer)
    image_data=buffer.getvalue()
    buffer.close()
    base64_data = base64.b64encode(image_data) #读取文件内容，转换为base64编码
        
    html_str = '<br><img src="data:image/png;base64,'+ base64_data + '"></div><br>'
    f.write(html_str)
    


def draw_barh(df,title,f):
    
    mpl.rcParams['font.sans-serif']=['Microsoft YaHei'] #用来正常显示中文标签 
    
    col_n = len(df.columns)
    row_n = len(df)    
    figsize = (8,min(8,np.float(row_n)/2))
    
    fig = plt.figure(figsize=figsize)
    plt.subplots_adjust(left=0.15, right=0.9, top=(1-0.6/figsize[1]), bottom=(0.6/figsize[1])) 
    ax1 = plt.subplot()
    #ax2 = ax1.twinx()
    plt.title(title)
    
    for i in range(col_n):
        xSeries = range(col_n - i - 1,row_n*(col_n+1),col_n+1)[::-1]
        ySeries = df[df.columns[i]]
        ax1.barh(xSeries, ySeries, label = df.columns[i])

    ax1.xaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.2f%%'))
    plt.yticks(np.array(xSeries) + 1 ,df.index) 
    plt.ylim((-1,row_n*(col_n+1)))
    
    ax1.grid(axis='x')
    ax1.legend(loc='upper right')
    
    # 输出到HTML   
    img2html(fig,f) 
    plt.close('all')
    

def draw_plot(title,df,format,f):

    mpl.rcParams['font.sans-serif']=['Microsoft YaHei'] #用来正常显示中文标签 
    
    fig = plt.figure(figsize=(10,5),dpi=100)
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
    ax1.legend(loc='upper left')
    
    img2html(fig,f) 
    plt.close('all')
    
def interest_curve(title,df,f):
    
    mpl.rcParams['font.sans-serif']=['Microsoft YaHei'] #用来正常显示中文标签
    
    fig = plt.figure(figsize=(10,5))
    plt.title(title)
    ax1 = plt.subplot()
    ax2 = ax1.twinx()
    
    #左坐标轴
    xSeries = range(11)
    ySeries = df[df.columns[0]]
    ymin = min(ySeries)
    ymax = max(ySeries)
    ax1.plot(xSeries, ySeries, label = df.columns[0].strftime("%Y%m%d"))
    ySeries = df[df.columns[1]]
    ymin = min(ymin,min(ySeries))
    ymax = max(ymax,max(ySeries))
    ax1.plot(xSeries, ySeries, '--', label = df.columns[1].strftime("%Y%m%d"))
    ySeries = df[df.columns[2]]
    ymin = min(ymin,min(ySeries))
    ymax = max(ymax,max(ySeries))
    ax1.plot(xSeries, ySeries, '--', label = df.columns[2].strftime("%Y%m%d"))
    
    ax1.set_ylim(ymin-2,ymax*1.1)
    
    #右坐标轴
    ySeries = np.array(df[df.columns[0]]-df[df.columns[1]])*100
    ymax = max(abs(np.array(ySeries)))
    ax2.bar(np.array(xSeries), ySeries, width=1.0/3*0.8, label = u'近1日基点变动 [bp][右]')
    ySeries = np.array(df[df.columns[0]]-df[df.columns[2]])*100
    ymax = max(abs(np.array(ySeries)))
    ax2.bar(np.array(xSeries)+1.0/3, ySeries, width=1.0/3*0.8, label = u'近5日基点变动 [bp][右]')
    
    ax2.set_ylim(-ymax*1.1,ymax*3)
    
    #坐标轴格式设置
    plt.xticks(xSeries, df.index)
    #ax1.xaxis.set_major_formatter(mpl.dates.DateFormatter('%y%m%d'))
    ax1.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.2f%%'))
    ax2.xaxis.set_ticks_position('bottom')
    ax2.spines['bottom'].set_position(('data', 0))
    
    ax1.grid(True)
    ax1.legend(loc = 'upper left')
    ax2.legend(loc = 'upper center')
    
    # 输出到HTML   
    img2html(fig,f) 
    plt.close('all')


