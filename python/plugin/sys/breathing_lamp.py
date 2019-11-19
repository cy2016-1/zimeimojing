# -*- coding: utf-8 -*-
from plugin import Plugin
import time,os
import multiprocessing as mp    #多进程
from package.base import Base, log
import RPi.GPIO as GPIO

class Breathing_lamp(Base,Plugin):


    def __init__(self, public_obj ):
        self.kill = mp.Value("h",0)  #定义全局共享内存
        self.go = mp.Value("h",0)  #定义全局共享内存


    def main(self,kill,go):
        channel = 15
        GPIO.setmode(GPIO.BOARD) #设置引脚编号规则
        GPIO.setup(channel, GPIO.OUT)   #引脚设置成输出模式
        self.go.value =1 #启动1
        while 1:

            GPIO.output(channel, 1)  
            time.sleep(1)
            GPIO.output(channel, 0)  
            time.sleep(1)
            if kill.value == 1: 
                go.value  = 0#关闭0
                kill.value  = 0
                break
        print("呼吸灯结束进程")

    def start(self,enobj):

        self.kill.value  = 0
        if self.go.value  == 0:
            m = mp.Process(target =lambda : self.main(self.kill,self.go) )
            m.start()
            return {'state':True,'data':"呼吸灯已经打开",'msg':'','stop':True}
        else:
            return {'state':True,'data':"呼吸灯已启动，可以说停止呼吸灯",'msg':'','stop':True}
    
    #停止
    def stop(self, enobj={}):
 
        if  self.go.value  == 1:
            self.kill.value  = 1           
            return {'state':True,'data':"呼吸灯已经取消",'msg':'','stop':True}
        else:
            return {'state':True,'data':"没有启动呼吸灯",'msg':'','stop':True}