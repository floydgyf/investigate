# -*- coding: utf-8 -*-
import win32com.client as win32 
from email.mime.multipart import MIMEMultipart  
from email.mime.text import MIMEText  
from email.mime.image import MIMEImage 
import time
import xlrd
import os

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
    mail.BCC = str

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
    

 