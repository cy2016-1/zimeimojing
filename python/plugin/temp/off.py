import os,time
from plugin import Plugin
from package.config import config           #导入固件配置
import multiprocessing as mp

class Off(Plugin):
    '''显示器控制类'''
    def __init__(self, public_obj):
        print(public_obj)
        self.is_pause  = mp.Value("h",0)

    def print_time(self, is_pause ):
        while 1:
            time.sleep(1)
            if is_pause.value==1:
                continue
            print('停止插件：'+ str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) )

    # 打开屏幕
    def start(self,name):
        self.pub = mp.Process(
            target = self.print_time,
            args = (self.is_pause,)
        )
        self.pub.start()
        self.is_pause.value = 0

    def pause(self):
        print('执行了停止插件中的-------------------暂停函数')
        self.is_pause.value = 1

    #插件继续
    def resume(self, sbobj={}):
        self.is_pause.value = 0

