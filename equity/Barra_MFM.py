# -*- coding: utf-8 -*-
from WindPy import *
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
import time
import os


def get_market_data(start_date,end_date):
    w.start()
    date_list = w.tdays(start_date, end_date, "").Times
    for date in date_list:
        sec_list = w.wset("sectorconstituent","date=" + date.strftime("%Y%m%d") + ";sectorid=a001010100000000").Data[1]
        var_list = ["pre_close","open","high","low","close","volume","amt","pct_chg","vwap","adjfactor","trade_status"]
        windout= w.wss(sec_list, var_list,"tradeDate="+ date.strftime("%Y%m%d") +";priceAdj=F;cycle=D")
        df = pd.DataFrame(windout.Data, columns = windout.Codes, index = windout.Fields).T
        df.to_csv("D:\\Investigate\\equity\\stock_A\\market_data\\"+date.strftime("%Y%m%d"), encoding='utf-8')
    w.close()

def market2db(start_date,end_date):
    import sqlite3
    conn = sqlite3.connect('D:\\Investigate\\data\\investigate.db')
    cur = conn.cursor()
    w.start()
    date_list = w.tdays(start_date, end_date, "").Times
    for date in date_list:
        sec_list = w.wset("sectorconstituent","date=" + date.strftime("%Y%m%d") + ";sectorid=a001010100000000").Data[1]
        var_list = ["pre_close","open","high","low","close","volume","amt","pct_chg","vwap","adjfactor","trade_status"]
        windout= w.wss(sec_list, var_list,"tradeDate="+ date.strftime("%Y%m%d") +";priceAdj=U;cycle=D")
        data = windout.Data
        var = windout.Fields
        data.insert(0,sec_list)
        data.insert(0,[date]*len(sec_list))
        var.insert(0,'SECCODE')
        var.insert(0,'DATE')
        df = pd.DataFrame(data, columns = windout.Codes, index = var).T
        df.to_sql(name='TMP', con=conn, if_exists='replace', index=False)
        cur.execute('''
            insert into MarketA 
            select 
                date
                ,seccode
                ,case when trade_status = "停牌一天" then NULL else pre_close end
                ,case when trade_status = "停牌一天" then NULL else open end
                ,case when trade_status = "停牌一天" then NULL else high end
                ,case when trade_status = "停牌一天" then NULL else low end
                ,close
                ,case when trade_status = "停牌一天" then NULL else volume end
                ,case when trade_status = "停牌一天" then NULL else amt end
                ,case when trade_status = "停牌一天" then NULL else pct_chg end
                ,case when trade_status = "停牌一天" then NULL else vwap end
                ,adjfactor
                ,trade_status
            from TMP as a
        ''')
        conn.commit()
    cur.close()
    conn.close()
    w.close()


def mrq(date):
    datetime = time.strptime(date,"%Y-%m-%d")
    if datetime.tm_mon in [1,2,3]:
        return str(datetime.tm_year-1) + '1231'
    elif datetime.tm_mon in [4,5,6]:
        return str(datetime.tm_year) + '0331'
    elif datetime.tm_mon in [7,8,9]:
        return str(datetime.tm_year) + '0630'
    else:
        return str(datetime.tm_year) + '0930'
    
def cal_descriptor(date):
    import sqlite3
    from scipy import stats 
    
    conn = sqlite3.connect('D:\\Investigate\\data\\investigate.db')
    cur = conn.cursor()
    conn_ram = sqlite3.connect(':memory:')
    cur_ram = conn_ram.cursor()
    ######Step1:检查数据完整性##########
      
          
    path = os.path.dirname(os.path.realpath(__file__))
    sec_list = w.wset("sectorconstituent","date=" + date + ";sectorid=a001010100000000").Data[1]
    mrq_date = mrq(date)
    
    #--------BETA & HSIGMA & DASTD & CMRA----------
    begdate = w.tdaysoffset(-252, date, "").Data[0][0].strftime("%Y-%m-%d")
    enddate = w.tdaysoffset(-1, date, "").Data[0][0].strftime("%Y-%m-%d")
    lambd63 = (np.ones(252) * 0.5**(1.0/63)) ** range(252)[::-1]
    lambd42 = (np.ones(252) * 0.5**(1.0/42)) ** range(252)[::-1]
    
    #样本日收益率
    cur.execute('''      
        select date, seccode, pct_chg
        from marketa
        where ? <= date and date <= ? 
        order by date asc
    ''',(begdate,enddate))
    col_name_list = [tuple[0] for tuple in cur.description]
    df = pd.DataFrame(cur.fetchall(), columns = col_name_list)
    df.to_sql('TMP',conn_ram, if_exists = 'replace', index = False)
    cur_ram.execute('CREATE INDEX sec_tmp ON TMP ( SECCODE )') 
    
    #市场日收益率
    market_return = w.wsd("000300.SH", "pct_chg", begdate, enddate, "PriceAdj=F").Data[0]
    market_return = np.array(market_return) * lambd63
    BETA = []
    HSIGMA = []
    DASTD = []
    CMRA = []
    for i in range(len(sec_list)):
        cur_ram.execute('select PCT_CHG from TMP where SECCODE = ?',(sec_list[i],))
        sec_return = pd.DataFrame(cur_ram.fetchall(), columns = ['PCT_CHG'])['PCT_CHG']
        if sec_return[0] == None:
            BETA.append(np.nan)
            HSIGMA.append(np.nan)
            DASTD.append(np.nan)
            CMRA.append(np.nan)
            continue
        if len(sec_return) < 252:
            sec_return = [np.nan] * (252-len(sec_return)) + list(sec_return)
        sec_return = np.array(sec_return)
        filter_list = ~np.isnan(sec_return)   
        if sum(filter_list) >= 50:
            x = sec_return[filter_list]
            weight = lambd42[filter_list]
            DASTD.append(sqrt(average((x-average(x, weights = weight))**2, weights = weight)))
            maxz = -9999
            minz = 9999
            s = 0
            for j in range(252)[::-1]:
                if not np.isnan(sec_return[j]):
                    s += log(1+sec_return[j]/100)
                if j%21 == 0:
                    if s > maxz:
                        maxz = s
                    if s < minz:
                        minz = s
            CMRA.append(maxz - minz) 
            xSeries = market_return[filter_list]
            ySeries = (sec_return * lambd63)[filter_list]
            res = stats.linregress(xSeries,ySeries)
            BETA.append(res.slope)
            HSIGMA.append(res.stderr)
        else:
            BETA.append(np.nan)
            HSIGMA.append(np.nan)
            DASTD.append(np.nan)
            CMRA.append(np.nan)
    
    #---------------Momentum----------------------
    begdate = w.tdaysoffset(-525, date, "").Data[0][0].strftime("%Y-%m-%d")
    enddate = w.tdaysoffset(-22, date, "").Data[0][0].strftime("%Y-%m-%d")
    lambd = ((np.ones(525) * 0.5**(1.0/126)) ** range(525))[:20:-1]
    
    #样本日收益率
    cur.execute('''      
        select date, seccode, pct_chg
        from marketa
        where ? <= date and date <= ? 
        order by date asc
    ''',(begdate,enddate))
    col_name_list = [tuple[0] for tuple in cur.description]
    df = pd.DataFrame(cur.fetchall(), columns = col_name_list)
    df.to_sql('TMP',conn_ram, if_exists = 'replace', index = False)
    cur_ram.execute('CREATE INDEX sec_tmp ON TMP ( SECCODE )') 
   
    #市场日收益率
    market_return = w.wsd("000300.SH", "pct_chg", begdate, enddate, "PriceAdj=F").Data[0]
    market_return = np.array(market_return)
    RSTR = []
    for i in range(len(sec_list)):
        cur_ram.execute('select PCT_CHG from TMP where SECCODE = ?',(sec_list[i],))
        sec_return = pd.DataFrame(cur_ram.fetchall(), columns = ['PCT_CHG'])['PCT_CHG']
        if sec_return[0] == None:
            RSTR.append(np.nan)
            continue
        if len(sec_return) < 504:
            sec_return = [np.nan] * (504-len(sec_return)) + list(sec_return)
        sec_return = np.array(sec_return)
        if sum(~np.isnan(sec_return)) >= 50:
            ans = (log(1+sec_return/100)-log(1+market_return/100))*lambd
            ans = ans[~np.isnan(ans)].sum()
            RSTR.append(ans)
        else:
            RSTR.append(np.nan)
    
    
    #SIZE & Non-linear Size
    tmp = w.wss(sec_list, "mkt_cap_ard","unit=1;tradeDate=" + date).Data[0]
    LNCAP = pd.DataFrame(np.log(tmp), columns = ["LNCAP"], index = sec_list)
    NLSIZE = pd.DataFrame(np.log(tmp)**3, columns = ["NLSIZE"], index = sec_list)
    
    #------------------------Earnings Yield & Book-to-Price---------------------
    #EPIBS    
    tmp = w.wss(sec_list, "pe_est,pe_ttm,pcf_ocf_ttm,pb_mrq","tradeDate="+ date +";year=" + date[0:4]).Data
    EPIBS = 1.0 / np.array(tmp[0])        
    #ETOP
    ETOP = 1.0 / np.array(tmp[1])
    #CETOP
    CETOP = 1.0 / np.array(tmp[2])
    #BTOP
    BTOP = 1.0 / np.array(tmp[3])
      
    
    #-------------------SGRO & EGRO & EGIBS & EGIBS_s--------------
    
    

    ###Leverage
    
    ###Liquidity
    #STOM
    start_date = w.tdaysoffset(-21, date, "").Data[0][0].strftime("%Y%m%d")
    STOM = w.wss(sec_list, "turn_free_per","startDate=" + start_date + ";endDate=" + date).Data[0]
    #STOQ
    start_date = w.tdaysoffset(-21, date, "").Data[0][0].strftime("%Y%m%d")
    STOQ = w.wss(sec_list, "turn_free_per","startDate=" + start_date + ";endDate=" + date).Data[0]
    #STOA
    start_date = w.tdaysoffset(-21, date, "").Data[0][0].strftime("%Y%m%d")
    STOA = w.wss(sec_list, "turn_free_per","startDate=" + start_date + ";endDate=" + date).Data[0]
    
    
    #columns = ['BETA','RSTR','LNCAP','EPIBS','ETOP','CETOP','DASTD','CMRA','HSIGMA','SGRO','EGRO','EGIBS','EGIBS_s','BTOP','MLEV','DTOA','BLEV','STOM','STOQ','STOA','NLSIZE']
    #data = [BETA, RSTR, LNCAP, EPIBS, ETOP, CETOP, DASTD, CMRA, HSIGMA, SGRO, EGRO, EGIBS, EGIBS_s, BTOP, MLEV, DTOA, BLEV, STOM, STOQ, STOA, NLSIZE]
    data = [BETA, CMRA, DASTD, HSIGMA]
    columns = ['BETA', 'CMRA', 'DASTD','HSIGMA']
    descriptor = pd.DataFrame(data, index = columns, columns = sec_list).T
    
    return descriptor

def stdfactor(df):
    col = df.columns
    para = pd.DataFrame(index = df.columns,columns = ['avg','std'])  
    for col in df.columns:
        x = df[col][~np.isnan(df[col])]
        para.loc[col,'avg'] = mean(x)
        para.loc[col,'std'] = std(x)
        df[col] = (np.array(df[col]) - para.loc[col,'avg']) / para.loc[col,'std']
    return para

def cal_factor(df):
    df_factor = pd.DataFrame(index = df.index, columns = ['Beta','Momentum','Size','Earning','Residual','Growth','BP','Leverage','Liquidity','NLSize'])
    df_industry = pd.DataFrame(index = df.index, columns = ['Beta','Momentum','Size','Earning','Residual','Growth','BP','Leverage','Liquidity','NLSize'])
    
    df_factor['Beta'] = df['BETA']
    df_factor['Momentum'] = df['RSTR']
    df_factor['Size'] = df['LNCAP']
    df_factor['Earning'] = 0.68 * df['EPIBS']+ 0.11 * df['ETOP']+ 0.21 * df['CETOP']
    df_factor['Residual'] = 0.74 * df['DASTD']+ 0.16 * df['CMRA']+ 0.1 * df['HSIGMA']
    df_factor['Growth'] = 0.47 * df['SGRO'] + 0.24 * df['EGRO'] + 0.18 * df['EGIBS'] + 0.11 * df['EGIBS_s'] 
    df_factor['BP'] = df['BTOP']
    df_factor['Leverage'] = 0.38 * df['MLEV'] + 0.35 * df['DTOA'] + 0.27 * df['BLEV'] 
    df_factor['Liquidity'] = 0.35 * df['STOM'] + 0.35 * df['STOQ'] + 0.3 * df['STOA'] 
    df_factor['NLSize'] = df['NLSIZE']


def cal_return():
    from sklearn.linear_model import LinearRegression  
    
    linreg = LinearRegression()  
    model = linreg.fit(x, y)  
    print model  
    print linreg.intercept_  
    print linreg.coef_  

def cal_cov(date):
    import numpy as np
    import sqlite3
    
    conn = sqlite3.connect('D:\\Investigate\\data\\investigate.db')
    cur = conn.cursor()
    #获取收益率序列
    cur.execute('''
        select * from FReturn where ? <= date and date <= ? 
    ''',(begdate,enddate))
    
    np.cov()