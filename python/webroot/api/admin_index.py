import json
import os
import re

from .ApiBase import ApiBase

class admin_index(ApiBase):

    def __init__(self, handler):
        super().__init__(handler)
 
    # 返回CPU温度信息
    def getCPUtemperature(self):
        res = os.popen('vcgencmd measure_temp').readline()
        return(res.replace("temp=","").replace("'C\n",""))
    
    # 返回内存使用情况 (单位=kb) 列表
    # Index 0: total RAM
    # Index 1: used RAM
    # Index 2: free RAM
    def getRAMinfo(self):
        p = os.popen('free')
        i = 0
        while 1:
            i = i + 1
            line = p.readline()
            if i==2:
                return(line.split()[1:4])
    
    # 返回CPU使用百分比%
    def getCPUuse(self):
        return(str(os.popen(r"top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip()))

    # 返回磁盘使用情况表
    # Index 0: total disk space
    # Index 1: used disk space
    # Index 2: remaining disk space
    # Index 3: percentage of disk used
    def getDiskSpace(self):
        p = os.popen("df -h /")
        i = 0
        while 1:
            i = i +1
            line = p.readline()
            if i==2:
                return(line.split()[1:5])

    # 转换磁盘大小
    def diskToNum(self, disknum):
        intnum = float(re.sub(r'G|T|K|B', '', disknum))
        renum = 0
        if re.search(r'G', disknum, re.M|re.I):
            renum = intnum * 1024 * 1024
        elif re.search(r'K', disknum, re.M|re.I):
            renum = intnum * 1024
        return renum


    # 返回所有信息
    def get_allinfo(self):
        cpu_temp  = self.getCPUtemperature()    # CPU温度
        cpu_usage = self.getCPUuse()            # CPU使用率
        if len(cpu_usage)<=0:
            cpu_usage = 1

        # 内存使用率
        ram_stats = self.getRAMinfo()
        ram_total = round(int(ram_stats[0]) / 1000,1)
        ram_used  = round(int(ram_stats[1]) / 1000,1)
        ram_ues   = int((ram_used / ram_total) * 100)

        # 磁盘使用率
        disk_stats = self.getDiskSpace()
        disk_total = disk_stats[0]
        disk_used  = disk_stats[1]

        disk_total = self.diskToNum(disk_total)
        disk_used  = self.diskToNum(disk_used)
        # disk_perc = disk_stats[3]
        disk_ues = int((disk_used / disk_total) * 100)
        # disk_ues = str(int(disk_total))

        new_json = {
            'cpuTemp': cpu_temp,
            'cpuUse': cpu_usage,
            'ramUse': ram_ues,
            'diskUes': disk_ues
        }
        ret_arr = {
            'code' : 20000,
            'message': '获取全部插件数据成功',
            'data': new_json
        }
        return json.dumps(ret_arr)

    def main(self):
        # 获取所有设备状态信息
        if self.query['op']=='getallinfo':
            return self.get_allinfo()

'''
if __name__ == '__main__':
    adm = admin_index()
        # CPU informatiom
    CPU_temp = adm.getCPUtemperature()
    CPU_usage = adm.getCPUuse()
    
    # RAM information
    # Output is in kb, here I convert it in Mb for readability
    RAM_stats = adm.getRAMinfo()
    RAM_total = round(int(RAM_stats[0]) / 1000,1)
    RAM_used = round(int(RAM_stats[1]) / 1000,1)
    RAM_free = round(int(RAM_stats[2]) / 1000,1)
    
    # Disk information
    disk_stats = adm.getDiskSpace()
    DISK_total = disk_stats[0]
    DISK_used = disk_stats[1]
    DISK_perc = disk_stats[3]

    print('')
    print('CPU Temperature = '+CPU_temp)
    print('CPU Use = '+CPU_usage)
    print('')
    print('RAM Total = '+str(RAM_total)+' MB')
    print('RAM Used = '+str(RAM_used)+' MB')
    print('RAM Free = '+str(RAM_free)+' MB')
    print('') 
    print('DISK Total Space = '+str(DISK_total)+'B')
    print('DISK Used Space = '+str(DISK_used)+'B')
    print('DISK Used Percentage = '+str(DISK_perc))

'''