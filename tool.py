#!/usr/bin/python3

import os
import requests
import json
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import time

import logging
from logging.handlers import TimedRotatingFileHandler

class Props():
    def __init__(self, configPath):
        self.configPath = configPath
        self.propMap = {}

    def loadProperties(self):
        openFile = open(self.configPath, 'r')
        for line in openFile:
            line = line.strip()
            if line.find('=') > 0 and not line.startswith('#'):
                strs = line.split('=', 1)
                self.propMap[strs[0].strip()] = strs[1].strip()
        return self

    def getValue(self, key):
        return self.propMap[key]


class DingDingMsg():
    def __init__(self):
        self.headers = {'Content-Type': 'application/json'}

    def sendMsg(self, webhook, content):
        data = {"msgtype": "text", "text": {"content": content}, "at":{"atMobiles":[],"isAtAll": True}}
        return requests.post(webhook, data=json.dumps(data), headers=self.headers)


class MailMsg():
    def __init__(self, host, port, sendername, password, receivers):
        self.smtpObj = smtplib.SMTP()
        self.smtpObj.connect(host, port)
        self.smtpObj.login(sendername, password)
        self.host = host
        self.port = port
        self.sendername = sendername
        self.password = password
        self.receivers = receivers

    def sendEmail(self, mailContent, subject):
        receiverList=self.receivers.split(",")

        message = MIMEText(mailContent, 'plain', 'utf-8')
        message['From'] = Header(self.sendername, 'utf-8')
        message['To'] = Header(','.join(receiverList), 'utf-8')
        message['Subject'] = Header(subject, 'utf-8')

        self.smtpObj.sendmail(self.sendername, receiverList, message.as_string())
        self.smtpObj.quit()

class ListUtil():
    def __init__(self):
        pass

    def appendAll(self,list,appendedList):
        if list == None or appendedList == None or len(appendedList) == 0:
            return

        while True:
            p=appendedList.pop()
            if p != None:
                list.append(p)
            if len(appendedList) == 0:
                break


class Logger():
    def __init__(self,name,propMap):
        formatStr='%(asctime)s %(levelname)s %(message)s'
        self.logger = logging.getLogger(name)
        filepath=propMap.getValue("log.path")
        filename=time.strftime(filepath+"/monitor.%Y%m%d.log",time.localtime())
        formatter = logging.Formatter(formatStr)
        self.logger.setLevel(logging.INFO)
        when=propMap.getValue("log.when")
        backupCount=int(propMap.getValue("log.backupcount"))
        th = TimedRotatingFileHandler(filename=filename,when=when,backupCount=backupCount,encoding='utf-8')
        th.setFormatter(formatter)
        ## 此处设置无论是debug还是info，都没有记录info消息，因此在上面设置了对应的level
        #th.setLevel(logging.DEBUG)
        self.logger.addHandler(th)
