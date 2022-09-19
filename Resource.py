#!/usr/bin/python3
import subprocess
import tool

class Top():
    def __init__(self,propMap,logger):
        self.propMap=propMap
        self.logger=logger
        self.topMap={}
    def loadInit(self):
        command = "top -bn 1 | head -n 1 | awk -F 'average:' '{print $2}'"
        top_stdout = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        topLoad = str(top_stdout.stdout.read().strip(), encoding="utf-8")
        self.logger.info("TopLoad: "+topLoad)
        loadArr = topLoad.split(",")
        self.topMap["load_1"] = loadArr[0]
        self.topMap["load_5"] = loadArr[1]
        self.topMap["load_15"] = loadArr[2]
        return self
    def topInit(self):
        command = "top -cbn 1 -w 30000"
        top_stdout = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        self.topRes = str(top_stdout.stdout.read().strip(), encoding="utf-8")


        self.logger.info(self.topRes)
        topArr=self.topRes.split("\n")
        line_0=topArr[0]
        loadStr=line_0.split("load average:")[1]
        loadArr=loadStr.split(",")
        self.topMap["load_1"]=loadArr[0]
        self.topMap["load_5"]=loadArr[1]
        self.topMap["load_15"]=loadArr[2]

        line_2=topArr[2].replace(",","")
        line2Arr=line_2.split()
        self.topMap["cpu_idl"]=line2Arr[7]

        line_3=topArr[3].replace(",","").replace(":","")
        line3Arr=line_3.split()
        self.topMap["mem_total"]=line3Arr[2]

        if "used" == line3Arr[5]:
            self.topMap["mem_used"]=line3Arr[4]
        elif "used" == line3Arr[7]:
            self.topMap["mem_used"]=line3Arr[6]


        if "free" == line3Arr[5]:
            self.topMap["mem_free"]=line3Arr[4]
        elif "free" == line3Arr[7]:
            self.topMap["mem_free"]=line3Arr[6]

        self.topMap["mem_buffers"]=line3Arr[8]

        line_4=topArr[4].replace(",","")
        line4Arr=line_4.split()
        self.topMap["mem_avail_swap"]=line4Arr[8]

        mem_real_available=float(self.topMap["mem_buffers"])+float(self.topMap["mem_avail_swap"])+float(self.topMap["mem_free"])
        mem_rela_available_percent=mem_real_available/(float(self.topMap["mem_total"]) + float(self.topMap["mem_avail_swap"]))*100

        self.topMap["mem_real_available"]=mem_real_available
        self.topMap["mem_rela_available_percent"]=round(mem_rela_available_percent,2)

        return self

    def checkAll(self):
        result=[]
        topLoadWhichminMonitorStr = self.propMap.getValue("top.load.whichmin.monitor")
        topLoadThreshold=self.propMap.getValue("top.load")

        loadList=self.checkLoad(topLoadWhichminMonitorStr, topLoadThreshold)

        listUtil=tool.ListUtil()
        listUtil.appendAll(result,loadList)

        cpuIdlThreshold=self.propMap.getValue("top.cpuidl")
        cpuIdlErrorObj=self.checkCpuIdl(cpuIdlThreshold)
        if cpuIdlErrorObj != None:
            result.append(cpuIdlErrorObj)

        memoryThreshold=self.propMap.getValue("top.mem.available.percent")
        memoryErrorObj=self.checkMemory(memoryThreshold)
        if memoryErrorObj != None:
            result.append(memoryErrorObj)

        return result


    def checkLoad(self,topLoadWhichminMonitorStr,threshold):
        topLoadMonitorList=topLoadWhichminMonitorStr.split(',')
        result=[]
        load_min='5'
        while True:
           if len(topLoadMonitorList)==0 or load_min == None:
               break;
           load_min = topLoadMonitorList.pop()
           if 5 == int(load_min):
               r = self.judgeLoad(self.topMap["load_5"], threshold, "load_5")
               if r != None:
                   result.append(r)

           elif 15 == int(load_min):
               r = self.judgeLoad(self.topMap["load_15"], threshold, "load_15")
               if r != None:
                   result.append(r)

           elif 1 == int(load_min):
               r = self.judgeLoad(self.topMap["load_1"], threshold, "load_1")
               if r != None:
                   result.append(r)


        return result

    def checkCpuIdl(self,threshold):
        if float(self.topMap["cpu_idl"]) < float(threshold):
            errorMap = {}
            errorMap["index"] = "cpu_idl"
            errorMap["currVal"] = self.topMap["cpu_idl"]
            errorMap["thVal"] = threshold
            return errorMap
        return None

    def checkMemory(self,threshold):
        if float(self.topMap["mem_rela_available_percent"]) < float(threshold):
            errorMap = {}
            errorMap["index"] = "top_memory_avaliable"
            errorMap["currVal"] = self.topMap["mem_rela_available_percent"]
            errorMap["thVal"] = threshold
            return errorMap
        return None



    def judgeLoad(self,loadVal,threshold,indexName):
        if float(loadVal) > float(threshold):
                errorMap={}
                errorMap["index"]=indexName
                errorMap["currVal"]=loadVal
                errorMap["thVal"]=threshold
                return errorMap
        return None

    def getTopStr(self):
        if len(self.topMap) == 0:
            return None

        topStr="----------------Top----------------\n"
        for key in self.topMap.keys():
            topStr=topStr+key+" = "+str(self.topMap[key])+"\n"
        return topStr
class Disk():
    def checkDf(self, propMap):
        command = "df"
        df_stdout = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        dfRes = str(df_stdout.stdout.read().strip(), encoding="utf-8")
        dfFilesystemList=propMap.getValue("df.Filesystem").split(",")
        dfResArr=dfRes.split("\n");
        self.dfList=[]
        for line in dfResArr:
            lineArr=line.split();
            if dfFilesystemList.count(lineArr[0]) >0:
                map = {}
                map["Filesystem"] = lineArr[0]
                map["Size"] = lineArr[1]
                map["Used"] = lineArr[2]
                map["Avail"] = lineArr[3]
                map["MountedOn"] = lineArr[5]
                map["UsePercent"] = lineArr[4]
                self.dfList.append(map)

        result = []
        usedPercentThreshold = float(propMap.getValue("df.used.percent"))
        for item in self.dfList:
            usedPercent = float(item["UsePercent"].replace("%",""))
            if usedPercent >= usedPercentThreshold:
                errorMap = {}
                errorMap["index"] = "FileSystem: " + item["Filesystem"] + ", UsePercent"
                errorMap["currVal"] = usedPercent
                errorMap["thVal"] = usedPercentThreshold
                result.append(errorMap)
        return result

    def getDiskStr(self):
        if len(self.dfList) == 0:
            return None

        disStr="--------------------- Disk Free-----------------------\n"
        for item in self.dfList:
            for key in item.keys():
                disStr=disStr+key+" = "+ str(item[key])
            disStr=disStr+"\n"
            # str=str+"Filesystem = "+item["Filesystem"]+", Size = "+item["Size"]+", Used = "+item["Used"]
            # str=str+", Avail = "+item["Avail"]+", MountedOn = "+item["MountedOn"]+", UsePercent = "+item["UsePercent"]+"\n"
        return disStr






