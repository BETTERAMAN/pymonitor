#!/usr/bin/python3

import tool
import Resource
import os
import sys

try:
    config_filename = "monitor.properties"
    curr_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
    cfile = curr_path + "/" + config_filename

    p = tool.Props(cfile).loadProperties()
    logger = tool.Logger("topPy", p).logger

    webhook = p.getValue("dingding.addr")
    dd = tool.DingDingMsg()

    host = p.getValue("mail.host");
    port = p.getValue("mail.port")
    sendername = p.getValue("mail.sendername")
    password = p.getValue("mail.password")
    receivers = p.getValue("mail.receivers")
    filepath = p.getValue("log.path")

    topObj = Resource.Top(p, logger).topInit()
    resultList = topObj.checkAll()

    dfObj = Resource.Disk()
    dfErrorList = dfObj.checkDf(p)

    listUtil = tool.ListUtil()
    listUtil.appendAll(resultList, dfErrorList)

    serverName = p.getValue("server.name")
    subject = p.getValue("mail.subject") + " - " + serverName

    dingdingAlarmMsg = ""
    if len(resultList) > 0:
        for iterm in resultList:
            dingdingAlarmMsg = dingdingAlarmMsg + "Server name: " + serverName + ", index: " + iterm[
                "index"] + ", index value: " + str(iterm["currVal"]) + ", threshold: " + str(iterm["thVal"]) + "\n"

        dd.sendMsg(webhook, dingdingAlarmMsg)

    ## 邮件需要发送
    diskStr = dfObj.getDiskStr()
    topStr = topObj.getTopStr()

    mailMsg = ""
    if diskStr != None:
        mailMsg = mailMsg + diskStr + "\n"

    if topStr != None:
        mailMsg = mailMsg + topStr + "\n"

    mailObj = tool.MailMsg(host, port, sendername, password, receivers)
    mailObj.sendEmail(mailMsg, subject)
    logger.info("check end.")
except Exception as e:
    logger.error(e)












