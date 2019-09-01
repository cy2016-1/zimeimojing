#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import re
import difflib

'''
比较两个文件是否相同
返回：True - 相同 / False - 不同
'''
def file_diff(file1,file2):
    if os.path.exists(file1)==False: return False
    if os.path.exists(file2)==False: return False
    a = open(file1, 'r').readlines()
    b = open(file2, 'r').readlines()
    diff = difflib.ndiff(a, b)
    is_diff=True
    for i in diff:
        if i.startswith('+') or i.startswith('-'):
            is_diff = False
    return is_diff


def main():
    root_path = os.path.dirname(os.path.dirname(__file__))

    conf_path = os.path.join(root_path,'data/conf/')

    create_ap = os.path.join(root_path,'bin/create_ap')

    # supplicant WiFi 配置模板文件
    temp_supplicant = os.path.join(conf_path,"wpa_supplicant.conf")
    # 系统配置文件
    sys_supplicant  = '/etc/wpa_supplicant/wpa_supplicant.conf'

    #========================【WiFi 配置重置】==================================
    if file_diff(temp_supplicant, sys_supplicant)==False:
        #print('不同')
        cmd ='sudo mv '+sys_supplicant+' '+sys_supplicant+'_bak &&sudo cp -f '+temp_supplicant+ ' '+sys_supplicant
        os.system(cmd)
        os.system('sudo chmod a+w '+sys_supplicant)
        os.system('sudo wpa_cli -i wlan0 reconfigure')      #重新导入配置文件，可以在调试时，修改配置文件后运行此命令，使配置文件生效

    #停用WiFi网卡
    os.system('sudo ifconfig wlan0 down')
    os.system('sudo killall udhcpc')
    os.system('sudo killall wpa_supplicant')

    # 停止已经开启的热点
    os.system('sudo '+create_ap+' --stop wlan0')

    # 结束所有create_ap相关的进程
    taskcmd = 'ps ax | grep create_ap'
    out = os.popen(taskcmd).readlines();               # 检测是否已经运行
    for line in out:
        pat = re.compile(r'(\d+)\s+\?\s+S\s+\d')
        res = pat.findall(line)
        if len(res)>0:
            os.system('kill '+ res[0]);

    print('OK')

if __name__ == '__main__':
    main()
