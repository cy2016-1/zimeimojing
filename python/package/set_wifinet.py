#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import re
import difflib
import json
import package.init_create_ap as init_create_ap

# 系统配置文件
sys_supplicant = '/etc/wpa_supplicant/wpa_supplicant.conf';

def main(set_json):
    init_create_ap.main()

    pass_temp = '''
network={
    ssid="%s"
    psk="%s"
}
'''

    if str(set_json['wifipass']) == "":
        set_json['wifipass'] = 'NONE'

    formated_str = pass_temp%(str(set_json['wifiname']), str(set_json['wifipass']))

    print(formated_str)

    fo = open(sys_supplicant, "a")
    fo.seek(0, 2)
    fo.write( str(formated_str) )
    fo.close()

    #重新导入配置
    os.system('sudo wpa_supplicant -B w -D wext -i wlan0 -c '+sys_supplicant);
    os.system('sudo wpa_cli -i wlan0 reconfigure')
    os.system('sudo wpa_cli -i wlan0 select_network 0')
    os.system('sudo wpa_cli -i wlan0 enable_network 0')
    os.system('sudo /etc/init.d/networking restart')
    os.system('sudo ifconfig wlan0 down')
    os.system('sudo ifconfig wlan0 up')

if __name__ == '__main__':
    main()
