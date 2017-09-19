from send_email_outlook import send_email_outlook
#from equity import industry
import os 
import time

path = os.path.dirname(os.path.realpath(__file__))


intraday = time.localtime(time.time())
if intraday.tm_wday == 4:
    #周报
    os.system("python " + path + "\\equity\\industry.py")
elif intraday.tm_mday == 1:
    #月报
else：
    #日报


to_list = ['fanwz@bosera.com']
att_list = ['D:\\Investigate\\equity\\files\\SWI_PEBand.html']
send_email_outlook(to_list,att_list)

