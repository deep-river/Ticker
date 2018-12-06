# -*- coding: utf-8 -*-
from smtplib import SMTP, SMTP_SSL
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime
from configparser import ConfigParser
ntf = ConfigParser()


class SendMail(object):

    def __init__(self):
        ntf.read('Notification_config.ini')
        self.host_server = ntf.get('Mail', 'Host_server')
        self.port = ntf.get('Mail', 'Port')
        self.method = ntf.get('Mail', 'Method')
        self.sender = ntf.get('Mail', 'Sender')
        self.password = ntf.get('Mail', 'Password')
        self.sender_mail = ntf.get('Mail', 'Sender_mail')
        self.receiver = ntf.get('Mail', 'Receiver')
        send_time = datetime.now().replace(microsecond=0).isoformat(' ')
        content = ntf.get('Mail', 'Content')
        if content:
            self.mail_content = send_time + u' Ticker日志：' + '\n' + content
        else:
            self.mail_content = send_time + u' Ticker日志：' + '\n' + u'''
            数据更新操作完成！
            '''
        self.mail_title = u'Ticker提醒邮件：' + str(datetime.now().hour) + u'点' + str(datetime.now().minute) +u'分  数据更新已完成'

    def send(self):
        if self.method == 'STARTTLS':
            smtp = SMTP(self.host_server, self.port)
            smtp.ehlo()
            smtp.starttls()
            smtp.set_debuglevel(0)
            smtp.login(self.sender_mail, self.password)

        elif self.method == 'SSL':
            smtp = SMTP_SSL(self.host_server, self.port)
            smtp.ehlo(self.host_server)
            smtp.set_debuglevel(0)
            smtp.login(self.sender_mail, self.password)

        msg = MIMEText(self.mail_content, "plain", 'utf-8')
        msg["Subject"] = Header(self.mail_title, 'utf-8')
        msg["From"] = self.sender_mail
        msg["To"] = self.receiver

        try:
            smtp.sendmail(self.sender_mail, self.receiver, msg.as_string())
            smtp.quit()
            print("Mail sent successfully.")
        except Exception:
            print("Mail sent error!")

#notification = SendMail()
#notification.send()


