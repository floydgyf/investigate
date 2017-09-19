# -*- coding: utf-8 -*-
#发送带附件邮件
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import time
import xlrd

def addimg(src,imgid):  
    fp = open(src, 'rb')  
    msgImage = MIMEImage(fp.read())  
    fp.close()  
    msgImage.add_header('Content-ID', imgid)  
    return msgImage  


def send_email(to_list, att_list):    

    #创建一个邮件实例
    msg = MIMEMultipart()

    #加邮件头
    msg['Subject'] = u"Investigate订阅推送-" + time.strftime("%Y%m%d")  
    msg['From'] = "vincent.fan.513@foxmail.com"
    str = ''
    for address in to_list:
        str = str + address + ';' 
    msg['To'] = str
    
    #邮件内容
    maintext = u'''<font size = "5" face = "Microsoft YaHei"><b>Investigate 订阅推送</b></font>
    <br>
    <br><font face = "Microsoft YaHei">    详细内容见附件。</font>
    '''
    msgtext = MIMEText(maintext,"html","utf-8")  
    msg.attach(msgtext)  
    #msg.attach(addimg("D:\\Investigate\\img\\weekly.png","weekly"))  
    
    #构造附件
    for i in range(len(att_list)):
        att = MIMEText(open(att_list[i], 'rb').read(), 'base64', 'gb2312')
        att["Content-Type"] = 'application/octet-stream'
        filename = att_list[i].split("\\")[-1]
        att["Content-Disposition"] = 'attachment; filename = "'+ filename +'"' #这里的filename可以任意写，写什么名字，邮件中显示什么名字
        msg.attach(att)

    #发送邮件
    mail_host="smtp.qq.com"  #设置服务器
    mail_user="vincent.fan.513@foxmail.com"    #用户名
    mail_pass="beabetterman880513"   #口令   
    server = smtplib.SMTP()
    server.connect(mail_host)
    server.login(mail_user,mail_pass) #XXX为用户名，XXXXX为密码
    server.sendmail(msg['From'], msg['To'],msg.as_string())
    server.quit()
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

send_email(to_list,att_list)