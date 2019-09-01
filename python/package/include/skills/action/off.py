import os,time
from package.include.skills.plugin import Plugin
from package.config import config           #导入固件配置
import multiprocessing as mp

class Off(Plugin):
    '''显示器控制类'''
    def __init__(self, public_obj):
        print(public_obj)

    def print_time(self):
        while 1:
            time.sleep(1)
            print('停止插件：'+ str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) )

    # 打开屏幕
    def load(self,name):
        pub = mp.Process(
            target = self.print_time
        )
        pub.start()

