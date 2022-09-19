#!/usr/bin/python3
import tool
import Resource
import os
import sys

logger=None
try:
    config_filename = "monitor.properties"
    curr_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
    cfile=curr_path+"/"+config_filename
    p = tool.Props(cfile).loadProperties()
    logger = tool.Logger("LoadMonitor", p).logger

    topLoadWhichminMonitorStr = p.getValue("top.load.whichmin.monitor")
    topLoadThreshold = p.getValue("top.load")
    topObj = Resource.Top(p, logger).loadInit()
    loadErrorList = topObj.checkLoad(topLoadWhichminMonitorStr, topLoadThreshold)
    if len(loadErrorList) > 0:
        command="python3 "+curr_path+"/checkAll.py"
        ## 负载超过门限，调用脚本，发告警，发邮件
        os.system(command)
except Exception as e:
    logger.warn(e)



