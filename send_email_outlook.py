# -*- coding: utf-8 -*-
import win32com.client as win32 
from email.mime.multipart import MIMEMultipart  
from email.mime.text import MIMEText  
from email.mime.image import MIMEImage 
import time
import xlrd

def addimg(src,imgid):  
    fp = open(src, 'rb')  
    msgImage = MIMEImage(fp.read())  
    fp.close()  
    msgImage.add_header('Content-ID', imgid)  
    return msgImage  

def send_email_outlook(to_list,att_list):
    #创建一个邮件实例
    outlook = win32.Dispatch('outlook.application') 
    mail = outlook.CreateItem(0)
    msg = MIMEMultipart()

    #加邮件头 
    mail.Subject = u"Investigate订阅推送-" + time.strftime("%Y%m%d")  
    str = ''
    for address in to_list:
        str = str + address + ';'
    mail.To = str

    #邮件内容
    mail.Body = u'''Investigate 订阅推送
    
        详细内容见附件。
    '''
    
    #构造附件
    for i in range(len(att_list)):
        mail.Attachments.Add(att_list[i])
            
    #发送邮件
    mail.Send()
    print '发送成功'
    

xlwb = xlrd.open_workbook(u'mail_config.xlsx')

ws = xlwb.sheets()[0]
to_list = []
for i in range(1,ws.nrows):
    to_list.append(ws.cell(i,0).value.encode('utf-8'))

ws = xlwb.sheets()[1]
att_list = []
for i in range(1,ws.nrows):
    att_list.append('D:\\Investigate\\files\\' + ws.cell(i,3).value.encode('utf-8'))

send_email_outlook(to_list,att_list)
 