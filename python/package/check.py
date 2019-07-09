import time,os,re
import multiprocessing as mp                            #多进程
import RPi.GPIO as GPIO
import psutil       #检测内存
from package.base import Base,log                       #基本类
import package.include.skills.action.screens as screens

class Check(Base):
    """设备检测类"""

    def __init__(self):
        self.is_bind = False        #是否启动用户绑定提示窗口
        #设置不显示警告
        #GPIO.setwarnings(False)

        #设置读取面板针脚模式
        GPIO.setmode(GPIO.BOARD)
        self.pin_pingmo_kg   = self.config['GPIO']['pingmo_kg']                 # 设置屏幕控制脚
        self.pin_pingmo_zt   = self.config['GPIO']['pingmo_zt']['pin']          # 获取屏幕开关状态脚
        self.pin_pingmo_open = self.config['GPIO']['pingmo_zt']['open']         # 获取屏幕开关状态 1 - 高电平，0 - 低电平
        self.pin_fengshan_kg = self.config['GPIO']['fengshan_kg']               # 降温风扇开关 0 - 为关闭此功能
        self.pin_fengshan_zt = 0

        self.pin_renti_tc    = self.config['GPIO']['renti_tc']['pin']           # 人体探测
        self.pin_renti_max_time = self.config['GPIO']['renti_tc']['max_time']

        GPIO.setup(self.pin_pingmo_kg,GPIO.OUT)                                 # 设置屏幕控制脚为输出
        GPIO.setup(self.pin_pingmo_zt,GPIO.IN)
        GPIO.setup(self.pin_renti_tc, GPIO.IN)
        GPIO.setup(self.pin_fengshan_kg,GPIO.OUT)

        self.ren_nk_time = 0            # 人体离开时间
        self.is_op_screen = True        # 是否操作屏幕

        #屏幕控制类
        self.screens = screens.Screen()
        self.screens.openclose_screen(1)        # 初始化打开屏幕


    #启用检测是否有用户
    def enable_bind(self):
        if self.is_bind == True:
            clientid = self.config['MQTT']['clientid']
            print( clientid )
            nav_json = {"event":"open","size":{"width":380,"height":380},"url":"bind_user.html?qr="+ clientid }
            self.Mqtt.send_nav( nav_json )
            self.is_bind = False

    #人体探测
    def detect_ren(self):
        if self.pin_renti_max_time == 0: return False
        is_face = os.path.join(self.config['root_path'],'data/is_face')

        NOW_TIME = int(time.time())                     # 当前时间
        ctime = NOW_TIME
        if os.path.isfile(is_face):
            ctime = int(os.stat(is_face).st_ctime)      # 获取文件创建时间

        if GPIO.input(self.pin_renti_tc) == True:
            '''高电平：有人'''
            self.ren_nk_time  = 0               # 第一次检测人离开时间，置0
            self.is_op_screen = True

            if (NOW_TIME - ctime) > self.pin_renti_max_time:
                self.screens.openclose_screen(1)
                os.remove(is_face)

        else:
            '''人离开'''
            if self.ren_nk_time == 0:
                self.is_op_screen = True
                self.ren_nk_time = NOW_TIME     # 第一次检测人离开时间
            else:
                if (NOW_TIME - self.ren_nk_time) > self.pin_renti_max_time and self.is_op_screen:
                    self.is_op_screen = False
                    self.screens.openclose_screen(0)

    #检测声卡
    def detect_cards(self):
        if re.search("wm8960", os.popen("cat /proc/asound/cards").read()) == None:
            return False
        else:
            print('有声卡')
            return True

    #检测摄像头
    def detect_video(self):
        if re.search("video0", os.popen("ls -al /dev/ | grep video").read()) == None:
            pass

    #检测内存
    def detect_memory(self):
        if int((psutil.virtual_memory()[1]/1000)/1000) < 200:
            print('内存过低')

    #监控CPU温度
    def detect_cpuwd(self):
        res = os.popen('vcgencmd measure_temp').readline()
        wdg = re.match( r"temp=(.+)\'C", res, re.M|re.I)
        if wdg.group(1):
            wd = float(wdg.group(1))
            if wd >= 65:
                if self.pin_fengshan_zt == 0:
                    self.pin_fengshan_zt = 1
                    GPIO.output( self.pin_fengshan_kg, GPIO.HIGH )

            if wd < 55:
                if self.pin_fengshan_zt == 1:
                    self.pin_fengshan_zt = 0
                    GPIO.output( self.pin_fengshan_kg, GPIO.LOW )
        del res,wdg,wd

    #开始启动
    def start(self):
        while True:
            #print('检测进程已经启动',self.uid )
            self.detect_ren()
            self.detect_cpuwd()
            time.sleep(3)


    def main(self):
        #启动监视进程
        mp.Process(target=self.start).start()

