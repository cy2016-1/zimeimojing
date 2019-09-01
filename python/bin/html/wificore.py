#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os,time
import re
import difflib

class Wificore():
    """核心配置类"""
    def __init__(self):
        #print('配置核心类已经初始化')
        self.root_path = os.path.dirname(os.path.dirname(__file__))
        self.create_ap = os.path.join(self.root_path,'create_ap')
        self.conf_path = os.path.join(self.root_path,'conf/')
        self.sys_supplicant  = '/etc/wpa_supplicant/wpa_supplicant.conf'
        self.serverip  = '10.0.0.1'
        self.wifi_name = 'HTTP://' + self.serverip
        self.wlan = 'wlan0'                 #配置默认网卡
        self.is_exit = False

    '''
    比较两个文件是否相同
    返回：True - 相同 / False - 不同
    '''
    def file_diff(self,file1,file2):
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

    #开启热点
    def start_ap(self):
        cmd = 'sudo '+ self.create_ap + ' -n --no-virt --redirect-to-localhost -g'+ self.serverip +' '+ self.wlan +' '+ self.wifi_name
        #print( cmd )
        os.popen( cmd, 'w', -1 )

    # 停止已经开启的热点
    def stop_ap(self):
        os.system('sudo '+ self.create_ap +' --stop '+ self.wlan)

        # 结束所有create_ap相关的进程
        taskcmd = 'ps ax | grep create_ap'
        out = os.popen(taskcmd).readlines();               # 检测是否已经运行
        for line in out:
            pat = re.compile(r'(\d+)\s+\?\s+S\s+\d')
            res = pat.findall(line)
            if len(res)>0:
                os.system('kill '+ res[0])


    #开启AP成功
    def start_ap_success(self):
        pass

    #查询热点开启状态
    def query_ap(self):
        cmd = 'sudo '+ self.create_ap +' --list-running'
        #print( cmd )
        try:
            fdata = os.popen(cmd).read()
            #print( fdata )
            if fdata:
                regExp = r'(\d+)\s+' + self.wlan
                res = re.search(regExp,fdata)
                if res:
                    #print( res.group(1) )
                    #开启成功
                    self.is_exit = True
                    self.start_ap_success()

                if self.is_exit == False:
                    time.sleep(1)
                    self.query_ap()
                else:
                    return
        except:
            pass

    #查询连接到热点的客户端
    def query_ap_clients(self):
        cmd = 'sudo '+ self.create_ap + ' --list-clients '+ self.wlan
        try:
            fdata = os.popen(cmd).read()
            if fdata:
                fdata = fdata.strip()
                if fdata=="":
                    return 'ERROR'      #出错了，告诉程序退出

                regExp = r'MAC\s+IP\s+Hostname'
                res = re.search( regExp, fdata , re.M|re.I)
                if res:
                    #有客户端连接
                    return 1
                else:
                    return 0
            else:
                return 0
        except:
            return 0

    '''
    检测无线网卡配置情况
    返回：
        True    --  配置成功
        False   --  配置失败
    '''
    def test_network(self):
        cmd = 'sudo wpa_cli -i '+ self.wlan +' status'
        fdata = os.popen(cmd).read()
        regExp = r'wpa_state\=COMPLETED'
        res = re.search( regExp, fdata , re.M|re.I)
        if res:
            return True
        else:
            return False


    #初始化网络状态
    def init_network(self):
        #========================【WiFi 配置重置】==================================
        os.system('sudo wpa_cli -i '+ self.wlan +' reconfigure')      #重新导入配置文件，可以在调试时，修改配置文件后运行此命令，使配置文件生效

        #停用WiFi网卡
        os.system('sudo ifconfig '+ self.wlan +' down')
        os.system('sudo killall udhcpc')
        os.system('sudo killall wpa_supplicant')

        # 停止已经开启的热点
        self.stop_ap()

        return True

    #重启网络
    def restart_network(self):
        os.system('sudo wpa_supplicant -B w -D wext -i '+self.wlan+' -c '+ self.sys_supplicant);
        os.system('sudo wpa_cli -i '+self.wlan+' reconfigure')
        os.system('sudo wpa_cli -i '+self.wlan+' select_network 0')
        os.system('sudo wpa_cli -i '+self.wlan+' enable_network 0')
        os.system('sudo /etc/init.d/networking restart')
        os.system('sudo ifconfig '+self.wlan+' down')
        os.system('sudo ifconfig '+self.wlan+' up')


    #配置WiFi
    def config_wifi(self,set_json):
        self.init_network()

         # supplicant WiFi 配置模板文件
        temp_supplicant = os.path.join(self.conf_path,"wpa_supplicant.conf")

        #========================【WiFi 配置重置】==================================
        if self.file_diff(temp_supplicant, self.sys_supplicant)==False:
            ##print('不同')
            os.system('sudo mv '+ self.sys_supplicant+' '+ self.sys_supplicant+'_bak')
            os.system('sudo cp -f '+temp_supplicant+ ' '+ self.sys_supplicant)
            os.system('sudo chmod a+w '+ self.sys_supplicant)

        pass_temp = '''
network={
    ssid="%s"
    psk="%s"
}
'''

        if str(set_json['wifipass']) == "":
            set_json['wifipass'] = 'NONE'

        formated_str = pass_temp%(str(set_json['wifiname']), str(set_json['wifipass']))

        fo = open(self.sys_supplicant, "a")
        fo.seek(0, 2)
        fo.write( str(formated_str) )
        fo.close()

        #重新导入配置
        self.restart_network()

        time.sleep(2)
        os.system('sudo reboot')

        return True
