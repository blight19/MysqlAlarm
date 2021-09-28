#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:yanshushuang
# datetime:2021/9/26

import smtplib
from email.mime.text import MIMEText
from email.header import Header
import json
from pathlib import Path
import time
from mako.template import Template

file_path = Path(__file__).parent

with open(file_path.joinpath("conf.json"), 'rb') as f:
    conf = json.load(f)


def mail_handler(host, parameter, current, threshold, th_type, tag="",logger=None):
    mail_host = conf.get("host")
    mail_user = conf.get("username")
    mail_password = conf.get("password")

    mail_sender = conf.get("username")
    mail_receiver = conf.get("receiver")

    mytemplate = Template(filename=str(file_path.joinpath('temp.html')))

    text = mytemplate.render(host=host, parameter=parameter, current=current,
                             threshold=threshold, th_type=th_type, tag=tag, alert_time=time.strftime('%m-%d %H:%M:%S'))
    message = MIMEText(text, 'html', 'utf-8')
    message['From'] = Header('Mysql报警', 'utf-8')  # 发送者
    message['Subject'] = 'Mysql报警'
    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
        smtpObj.login(mail_user, mail_password)
        smtpObj.sendmail(mail_sender, mail_receiver, message.as_string())
        logger.info(f"{host} 邮件发送成功")
    except smtplib.SMTPException:
        logger.error(f"{host} Error: 无法发送邮件")


if __name__ == '__main__':
    host = "1.1.1.1"
    parameter = "Table_open_cache_hits_precent"
    current = "58.59"
    threshold = "80"
    th_type = "lt "
    mail_handler(host, parameter, current, threshold, th_type=th_type,tag="这里是Tag")
