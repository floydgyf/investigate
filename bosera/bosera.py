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
    

   
      
            
tmp = w.start()
intraday = time.strftime("%Y%m%d")
trade_day = w.tdaysoffset(-1, intraday, "").Data[0][0].strftime("%Y%m%d")
 

import sqlite3
conn = sqlite3.connect(':memory:')
cur = conn.cursor()
   
#债券分类（Wind）：一般企业债
sec_list = w.wset("sectorconstituent","date=" + trade_day + ";sectorid=1000004568000000").Data[1]
windout = w.wss(sec_list, "windcode,industry_sw,industry_CSRC12,amount,latestissurercreditrating,ptmyear,yield_cnbd","industryType=1;tradeDate=" + trade_day + ";credibility=1").Data
df = pd.DataFrame(windout, index = ['WindCode','IndustrySW','IndustryCSRC','RatingBond','RatingIssure','PTMYear','YTM']).T
df.to_sql(name='TMP', con=conn, if_exists='replace', index=False)

#债券分类（Wind）：一般公司债
sec_list = w.wset("sectorconstituent","date=" + trade_day + ";sectorid=1000009966000000").Data[1]
windout = w.wss(sec_list, "windcode,industry_sw,industry_CSRC12,amount,latestissurercreditrating,ptmyear,yield_cnbd","industryType=1;tradeDate=" + trade_day + ";credibility=1").Data
df = pd.DataFrame(windout, index = ['WindCode','IndustrySW','IndustryCSRC','RatingBond','RatingIssure','PTMYear','YTM']).T
df.to_sql(name='TMP', con=conn, if_exists='append', index=False)

#债券分类（Wind）：一般中期票据
sec_list = w.wset("sectorconstituent","date=" + trade_day + ";sectorid=1000004570000000").Data[1]
windout = w.wss(sec_list, "windcode,industry_sw,industry_CSRC12,amount,latestissurercreditrating,ptmyear,yield_cnbd","industryType=1;tradeDate=" + trade_day + ";credibility=1").Data
df = pd.DataFrame(windout, index = ['WindCode','IndustrySW','IndustryCSRC','RatingBond','RatingIssure','PTMYear','YTM']).T
df.to_sql(name='TMP', con=conn, if_exists='append', index=False)

#债券分类（Wind）：一般短期融资券
sec_list = w.wset("sectorconstituent","date=" + trade_day + ";sectorid=1000004566000000").Data[1]
windout = w.wss(sec_list, "windcode,industry_sw,industry_CSRC12,amount,latestissurercreditrating,ptmyear,yield_cnbd","industryType=1;tradeDate=" + trade_day + ";credibility=1").Data
df = pd.DataFrame(windout, index = ['WindCode','IndustrySW','IndustryCSRC','RatingBond','RatingIssure','PTMYear','YTM']).T
df.to_sql(name='TMP', con=conn, if_exists='append', index=False)

cur.execute(
'''
    create table Bond_Sample as 
    select 
        WindCode, 
        IndustryCSRC as Industry,
        case when RatingBond in("AAA","AA+","AA") then RatingBond else "AA-及以下" end as Rating, 
        case when PTMYear<1 then "1年以内" when 1<=PTMYear and PTMYear<3 then "1-3年" when 3<=PTMYear and PTMYear<7 then "3-7年" else "7年以上" end  as PTM,
        YTM,
        PTMYear
    from TMP
    where IndustryCSRC is not NULL and YTM is not NULL
    order by Industry, Rating, PTM
''')
cur.execute("select * from Bond_Sample")
col_name_list = [tuple[0] for tuple in cur.description]
df = pd.DataFrame(cur.fetchall(), columns = col_name_list)

last=[df['Industry'][0],df['Rating'][0],df['PTM'][0]]
YTM = []
data = []
for i in range(len(df)):
    if [df['Industry'][i],df['Rating'][i],df['PTM'][i]] <> last or i == len(df)-1:
        out = [len(YTM),mean(YTM)]
        for j in range(11):
            out.append(percentile(YTM,j*10))
        data.append(last+out)
        last = [df['Industry'][i],df['Rating'][i],df['PTM'][i]]
        YTM = [df["YTM"][i]]
    else:
        YTM.append(df["YTM"][i])
df = pd.DataFrame(data)
df.to_csv('D:\\test.csv', encoding = "utf-8-sig")

cur.close()
conn.close()