import logging
import os
import re
import time
from threading import Thread
from urllib.request import Request, urlopen
import RPi.GPIO as GPIO
from MsgProcess import MsgProcess, MsgType
from python.bin.Device import Device
from python.package.Mylib import Mylib
from python.module.WebApi.hefeng import hefeng


class Daemon(MsgProcess):
    ''' 守护进程初始化环境并监测网络连接CPU温度内存容量等内容'''
    def __init__(self, msgQueue):
        super().__init__(msgQueue)
        self.netStatus = False                                          # true为连网 false断网
        self.connectedTime = time.time()                                # 网络连网时间
        self.isScreen = self.config['LoadModular']['Screen']            # 是否有屏幕
        self.pin_setnet = self.config['GPIO']['setnet_pin']             # 配网控制（引脚定义）
        self.pin_fan_kg = self.config['GPIO']['fan_kg']                 # 降温风扇开关 0 - 为关闭此功能
        self.cputemp_high = self.config['GPIO']['cputemp']['high']      # CPU最高温度
        self.cputemp_low  = self.config['GPIO']['cputemp']['low']       # CPU最低温度
        self.playreadygo = True
        self.playno_network = True
        self.arr_setnet = []                                            # 配网按键控制
        self.isSettingNet = False                                       # 是否正在配网中
        self.pin_fengshan_zt = 0
        self.set_time_i = 100                                           # 设置时间计时
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pin_fan_kg, GPIO.OUT)
        GPIO.setup(self.pin_setnet, GPIO.IN)

    def detect_setnet(self):
        ''' 检测配网按键 '''
        # if not self.isSettingNet and self.netStatus is False:
        if not self.isSettingNet:
            st = GPIO.input(self.pin_setnet)
            if int(st) == 1:
                self.arr_setnet.append('1')
            else:
                self.arr_setnet.clear()

            if len(self.arr_setnet) >= 5:
                self.isSettingNet = True
                os.system("sudo rfkill unblock wifi && sudo rfkill unblock all")
                if self.config['initWifi'] == 'SoundWave':
                    self.send(MsgType.Stop, Receiver="Awake")
                    from python.bin.setWifi.soundSetNet import soundSetNet
                    soundSetNet()
                    return

                if self.config['initWifi'] == 'ApHot':
                    from python.bin.Setnet import Setnet
                    Netst = Setnet(self.config).main()
                    if Netst:
                        self.send(MsgType.Start, Receiver='MqttProxy')  # 启动mqtt
                    return

    def Start(self, message):
        ''' 起动守护线程 '''
        Thread(target=self.detectAll, args=(), daemon=True).start()

    def setCity(self):
        '''取如果全局配置没有城市数据 则设置城市位置'''
        config = Mylib.getConfig()                  # 取全局配置
        if config['LOCATION']['city'] is None:
            data = hefeng().get_city()
            if data:
                re_json = {'city': data['name'], 'city_cnid': data['id']}
                config['LOCATION']['city'] = re_json['city']
                config['LOCATION']['city_cnid'] = re_json['city_cnid']
                Mylib.saveConfig(config)             # 保存配置
            else:
                return False
        return True

    def detect_netstate(self):
        '''  监控网络状态 '''
        url = self.config['httpapi'] + r'/raspberry/ping.html'
        try:
            req = Request(url)
            f = urlopen(req, timeout=10)
            if f.getcode() == 200:
                self.set_time_i += 1
                if self.set_time_i > 100:
                    systime = f.read().decode()
                    systime = int(systime) + 1      # 偏移1秒
                    systime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(systime))
                    os.popen('sudo date -s "'+ systime +'"')
                    self.set_time_i = 0
                # print( systime )
                # data = {'type': 'dev', 'data':  {"netstatus": 1}}
                # if self.isScreen is True:
                #     self.send(MsgType.Text, Receiver='Screen', Data=data)
                self.connectedTime = time.time()
                if not self.netStatus:
                    self.netStatus = True
                    if self.isScreen is True:
                        data = {'type': 'dev', 'data':  {"netstatus": 1}}
                        self.send(MsgType.Text, Receiver='Screen', Data=data)
                        self.send(MsgType.Text, Receiver='Screen', Data='网络已连接')
                    logging.info('网络已连接')
                    if Device.online():                                 # 设备成功上线
                        self.setCity()                                  # 设置默认城市
                        self.send(MsgType.Start, Receiver='MqttProxy')  # 启动mqtt
                    if self.playreadygo:
                        # 准备好了。可以互动了
                        self.playreadygo = False
                        path = 'data/audio/readygo.wav'
                        os.system('aplay -q ' + path)
                return
        except Exception as e:
            logging.warning(e)
        if time.time() - self.connectedTime > 30:
            if self.playno_network:
                self.playno_network = False
                path = 'data/audio/meiyou_wangluo.wav'
                os.system('aplay -q ' + path)
            self.netStatus = False
            if self.isScreen is True:
                data = {'type': 'dev', 'data': {"netstatus": 0}}
                self.send(MsgType.Text, Receiver='Screen', Data=data)
                self.send(MsgType.Text, Receiver='Screen', Data='网络断开连接')
            logging.warning('网络断开连接')

    def detect_cpuwd(self):
        ''' 监控CPU温度 '''
        res = os.popen("cat /sys/class/thermal/thermal_zone0/temp").readline()
        wd = int(res) / 1000
        if wd >= self.cputemp_high:
            if self.pin_fengshan_zt == 0:
                self.pin_fengshan_zt = 1
                GPIO.output(self.pin_fan_kg, GPIO.HIGH)
                logging.info('启动CPU风扇')
        if wd < self.cputemp_low:
            if self.pin_fengshan_zt == 1:
                self.pin_fengshan_zt = 0
                GPIO.output(self.pin_fan_kg, GPIO.LOW)
                logging.info('关闭CPU风扇')
        return res


    def detectAll(self):
        time.sleep(5)               # 等待屏幕启动，以免丢失网络图标
        Device.setSoundCard()       # 设置默认声卡
        ''' 无限循环依次执行allTasks中的任务。每个任务执行后睡眠秒数 '''
        allTasks = [
            {'name': 'detect_netstate', 'sleep': 5},
            {'name': 'detect_cpuwd', 'sleep': 28},
            {'name': 'detect_setnet', 'sleep': 1}
        ]
        i = 0
        taske_i = [0]*len(allTasks)
        while True:
            for i in range(len(taske_i)):
                taske_i[i] += 1

                if taske_i[i] == allTasks[i]['sleep']:
                    eval('self.'+allTasks[i]['name']+'()')
                    taske_i[i] = 0

            time.sleep(1)

