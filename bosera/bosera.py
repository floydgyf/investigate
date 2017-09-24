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

def fetchdata(proc,  parameter):    
    import pymssql
    data = []
    conn=pymssql.connect(host='ia',database='ia')
    cur=conn.cursor()
    sql = u'exec '+ proc +' '
    for p in parameter:
        sql = sql + p[0] + '=' + p[1] + ','
    sql = sql[:-1].encode('utf-8')
    cur.execute(sql)
    
    while True:
        tmp = cur.fetchall()
        if tmp == []:
            break
        else:
            df = pd.DataFrame(tmp)
            data.append(df)
            cur.nextset()    
    
    cur.close()
    conn.close()
    return data


def hoding_chg(begdate,enddate):
    import sqlite3
    conn = sqlite3.connect(':memory:')
    cur = conn.cursor()
    #起始日持仓
    proc = u'p_报表_组合比例_多基金'
    para = []
    para.append(('@p_type',u'"组合个股"'))
    para.append(('@p_fund',u'"_所有组合"'))
    para.append(('@p_date','"'+ begdate +'"'))
    data = fetchdata(proc,para)[0]

    data.columns = ['FundName','SecCode','SecName','QuantNormal','QuantLimit','Cost','Profit','CostAmt','Return','Price','Amt','Proportion']
    data2 = data.copy()
    data[['QuantNormal','QuantLimit','Cost','Profit','CostAmt','Return','Price','Amt','Proportion']] = data2[['QuantNormal','QuantLimit','Cost','Profit','CostAmt','Return','Price','Amt','Proportion']].astype('float')
    data.to_sql(name='TMP', con=conn, if_exists='replace', index=False)
    
    cur.execute(
    '''
        create table BegHoding as 
        select FundName, SecCode, SecName, sum(QuantNormal+QuantLimit) as Quant,  sum(Price*(QuantNormal+QuantLimit))/sum(QuantNormal+QuantLimit) as Price, sum(Amt) as Amt
        from TMP
        where SecCode <> ""
        group by FundName, SecCode, SecName
    '''
    )
    
    #截止日持仓
    proc = u'p_报表_组合比例_多基金'
    para = []
    para.append(('@p_type',u'"组合个股"'))
    para.append(('@p_fund',u'"_所有组合"'))
    para.append(('@p_date','"'+ enddate +'"'))
    data = fetchdata(proc,para)[0]
    
    data.columns = ['FundName','SecCode','SecName','QuantNormal','QuantLimit','Cost','Profit','CostAmt','Return','Price','Amt','Proportion']
    data2 = data.copy()
    data[['QuantNormal','QuantLimit','Cost','Profit','CostAmt','Return','Price','Amt','Proportion']] = data2[['QuantNormal','QuantLimit','Cost','Profit','CostAmt','Return','Price','Amt','Proportion']].astype('float')
    data.to_sql(name='TMP', con=conn, if_exists='replace', index=False)
    
    cur.execute(
    '''
        create table EndHoding as 
        select FundName, SecCode, SecName, sum(QuantNormal+QuantLimit) as Quant,  sum(Price*(QuantNormal+QuantLimit))/sum(QuantNormal+QuantLimit) as Price, sum(Amt) as Amt
        from TMP
        where SecCode <> ""
        group by FundName, SecCode, SecName
    '''
    )
    
    #组合变动分析
    
    cur.execute(
    '''
        create table List as 
        select distinct *
        from (
            select FundName, SecCode, SecName from BegHoding
            union
            select FundName, SecCode, SecName from EndHoding )
    ''')
    cur.execute(
    '''
        create table Hoding_chg as
        select c.FundName, replace(c.SecCode,".SS",".SH") as SecCode, c.SecName, ifnull(a.Quant,0)-ifnull(b.Quant,0) as Chg, a.Quant as EndQuant, b.Quant as BegQuant, a.Price as EndPrice, b.Price as BegPrice 
        from 
            (List as c left join EndHoding as a on a.FundName=c.FundName and a.SecCode=c.SecCode and a.SecName=c.SecName) 
            left join BegHoding as b on b.FundName=c.FundName and b.SecCode=c.SecCode and b.SecName=c.SecName      
    ''')
    cur.execute(
    '''
        create table Sec_chg as
        select SecCode, SecName, sum(case when Chg>0 then Chg else 0 end) as Buy, sum(case when Chg<0 then Chg else 0 end) as Sell, sum(Chg) as Chg
        from Hoding_chg
        group by SecCode, SecName
        having sum(Chg)<>0
    ''')
    cur.execute('select * from Sec_chg')
    col_name_list = [tuple[0] for tuple in cur.description]
    df = pd.DataFrame(cur.fetchall(), columns = col_name_list)
    data = w.wss(list(df['SecCode']), "industry_citic,vwap_per","tradeDate="+enddate+";industryType=1;startDate="+begdate+";endDate="+enddate).Data
    df[['Industry','Price']]= pd.DataFrame(data).T
    df.to_sql(name='Sec_chg', con=conn, if_exists='replace', index=False)
    cur.execute(
    '''
        create table Industry_chg as
        select Industry, sum(Buy*Price)/10000 as Buy, sum(Sell*Price)/10000 as Sell, sum(Chg*Price)/10000 as Chg
        from Sec_chg
        group by Industry
        having Industry <> "None"
        order by Chg desc
    ''')
    cur.execute('select * from Industry_chg')
    col_name_list = [tuple[0] for tuple in cur.description]
    df = pd.DataFrame(cur.fetchall(), columns = col_name_list)
    cur.close()
    conn.close()
    return df
    

def industry_chg(df):
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    mpl.rcParams['font.sans-serif']=['Microsoft YaHei'] #用来正常显示中文标签 
    figsize = (8,8)
    fig = plt.figure(figsize=figsize)
    plt.subplots_adjust(left=0.15, right=0.9, top=(1-0.6/figsize[1]), bottom=(0.6/figsize[1])) 
    ax1 = plt.subplot()
    #ax2 = ax1.twinx()
    plt.title(u'中信行业持仓变化')
    
    xSeries = range(len(df))[::-1]
    ySeries = df[df.columns[1]]
    ax1.barh(xSeries, ySeries, height=0.8, label = u'买入（万）')
    ySeries = df[df.columns[2]]
    ax1.barh(xSeries, ySeries, height=0.8, color = 'green', label = u'卖出（万）')
    ySeries = df[df.columns[3]]
    ax1.barh(xSeries, ySeries, height=0.5, color = 'red', label = u'净买入（万）')
    
    ax1.xaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.2f'))
    plt.yticks(np.array(xSeries) ,df[df.columns[0]]) 
    plt.ylim((-1,len(df)))
    
    ax1.grid(axis='x')
    ax1.legend(loc='upper left')
    
    fig.show()