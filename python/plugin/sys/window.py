# -*- coding: utf-8 -*-
from plugin import Plugin
import time,os
import multiprocessing as mp    #多进程
import RPi.GPIO as GPIO

class Window(Plugin):


    def __init__(self, public_obj ):

        self.stepPin = 15
        self.dirPin = 36
        GPIO.setmode(GPIO.BOARD) #设置引脚编号规则
        GPIO.setup(self.stepPin, GPIO.OUT)   #将引脚设置成输出模式
        GPIO.setup(self.dirPin, GPIO.OUT)   #将引脚设置成输出模式





    def main(self,off_on):
    
        #使马达能够朝特定方向移动
        GPIO.output(self.dirPin, off_on)
        #为一个完整的循环旋转产生200个脉冲
        for x in range(200):

            GPIO.output(self.stepPin, 1)
            time.sleep(0.01)
            GPIO.output(self.stepPin, 0)
            time.sleep(0.01)        
                
            
    

    #开始
    def start(self,enobj):

        m=mp.Process(target =lambda : self.main(1) )
        m.start()
        return {'state':True,'data':"窗帘已经打开",'msg':'','stop':True}

    
    #停止
    def stop(self):
        m=mp.Process(target =lambda : self.main(0) )
        m.start()
        return {'state':True,'data':"窗帘已经关闭",'msg':'','stop':True} 














































    
    