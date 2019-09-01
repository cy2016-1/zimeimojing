import os,time
import RPi.GPIO as GPIO
from package.config import config           #导入固件配置
from plugin import Plugin
class Screens(Plugin):
    '''显示器控制类'''
    def __init__(self, public_obj):
        #设置不显示警告
        GPIO.setwarnings(False)

        self.pin_pingmo_kg   = config['GPIO']['pingmo_kg']               # 设置屏幕控制脚
        self.pin_pingmo_zt   = config['GPIO']['pingmo_zt']['pin']        # 获取屏幕开关状态
        self.pin_pingmo_open = config['GPIO']['pingmo_zt']['open']       # 屏幕开状态电平值

    '''
    开关显示器（硬件开关）
    isst - 1 / 0 ： 开 / 关
    '''
    def openclose_screen(self, isst = 1):
        screen_sw = GPIO.input(self.pin_pingmo_zt)

        if isst == 1:
            if int(screen_sw) != self.pin_pingmo_open:
                GPIO.output(self.pin_pingmo_kg,GPIO.HIGH)
                time.sleep(1)
                GPIO.output(self.pin_pingmo_kg,GPIO.LOW)

        elif isst == 0:
            if int(screen_sw) == self.pin_pingmo_open:
                GPIO.output(self.pin_pingmo_kg,GPIO.HIGH)
                time.sleep(1)
                GPIO.output(self.pin_pingmo_kg,GPIO.LOW)

    #mqtt 直接操作该函数控制
    def main(self,data):
        if data == "off":
            self.openclose_screen(0)
            return {'state':True,'data': "屏幕已经关闭",'msg':'参数1，需要输入off。字符串类型！','stop':True}
        elif data == 'on':
            self.openclose_screen(1)
            return {'state':True,'data': "屏幕已经打开",'msg':'参数1，需要输入on。字符串类型！','stop':True}

    #屏幕当前状态
    def init_screen(self):
        screen_sw = GPIO.input(self.pin_pingmo_zt)
        return str( screen_sw )

    #语音控制
    def start(self,name):
 #       print( name ,"我被调用了")
        # 打开屏幕 或者 关闭屏幕
        if name["trigger"] in ["屏幕点亮","打开屏幕","打开显示"]:
                return self.main("on")
        if name["trigger"] in ["关闭屏幕","屏幕关闭","关闭显示"]:
                return self.main("off")






if __name__ == '__main__':
    Screen().init_screen()
    quit()
    while 1:
        Screen().main('off')
        time.sleep(2)
        Screen().main('on')
        time.sleep(2)
