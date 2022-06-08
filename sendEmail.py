import smtplib
from email.mime.text import MIMEText

def sendMail(subject, content, receivers):
    #设置服务器所需信息
    #163邮箱服务器地址
    mail_host = 'smtp.163.com'

    mail_user = 'xxx'  #163用户名
    mail_pass = 'xxxx'   #密码(部分邮箱为授权码)

    sender = 'xxx@163.com'  #邮件发送方邮箱地址

    #设置email信息
    message = MIMEText(content, 'plain', 'utf-8') #邮件内容设置
    message['Subject'] = subject #邮件主题
    message['From'] = sender #发送方信息
    message['To'] = receivers[0] #接受方信息

    #登录并发送邮件
    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host, 25) #连接到服务器
        smtpObj.login(mail_user, mail_pass) #登录到服务器
        #发送
        smtpObj.sendmail(
            sender, receivers, message.as_string())
        #退出
        smtpObj.quit()
        print('success')
    except smtplib.SMTPException as e:
        print('error', e) #打印错误
