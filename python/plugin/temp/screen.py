import os,time
from plugin import Plugin
from package.config import config           #导入固件配置
import multiprocessing as mp

import threading

class Job(threading.Thread):

    def __init__(self, *args, **kwargs):
        super(Job, self).__init__(*args, **kwargs)
        self.__flag = threading.Event()     # 用于暂停线程的标识
        self.__flag.set()       # 设置为True
        self.__running = threading.Event()      # 用于停止线程的标识
        self.__running.set()      # 将running设置为True

    def run(self):
        while self.__running.isSet():
            self.__flag.wait()      # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
            print('屏幕插件：',time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            time.sleep(1)

    def pause(self):
        self.__flag.clear()     # 设置为False, 让线程阻塞

    def resume(self):
        self.__flag.set()    # 设置为True, 让线程停止阻塞

    def stop(self):
        self.__flag.set()       # 将线程从暂停状态恢复, 如何已经暂停的话
        self.__running.clear()        # 设置为False

class Screen(Plugin):
    '''显示器控制类'''
    def __init__(self, public_obj):
        print(public_obj)
        self.a = Job()


    def pause(self):
        print('执行了屏幕里的暂停'*10)
        self.a.pause()

    def resume(self, enobj ):
        print('执行了屏幕里的继续'*10)
        self.a.resume()


    # 打开屏幕
    def start(self,name):
        #self.a.start()
        while 1:
            time.sleep(1)
            print('屏幕插件：'+ str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) )

