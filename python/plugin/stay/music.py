import requests,os,time,re,string,math,random,pygame,threading,random
import multiprocessing as mp    #多进程
from plugin import Plugin
from package.base import Base       #基本类

class Music(Base, Plugin):

    def __init__(self,public_obj):

        self.music_path = '/music/'
        #检查根目录下有没有音乐文件夹
        if os.path.exists(self.music_path) ==False:
            os.mkdir(self.music_path)

        self.public_obj = public_obj

    #发送文字到屏幕
    def postmojing(self,data):
        try:
            self.public_obj.sw.send_info( {'obj':'mojing','msg': data} )
        except:
            pass

    #当前音量
    def voices(self):
        jieguo,jiance=str(),'['
        huoqu_os=os.popen("sudo amixer scontents | grep 'Front Left: Playback'|grep 'dB'").read()
        for x in re.sub(r'^.*k','',re.sub(r'].*$','',huoqu_os[len(re.sub(r'F.*$','',huoqu_os)):])):
            if x==jiance:
                jiance="kaishi"
            elif jiance=="kaishi":
                jieguo+=x
        #通过y = 1.7972e^(0.04x) x为填入的音量，y为实际音量 这个公式计算出实际音量。
        return 1.7972 * math.pow(2.718,0.04 * int(jieguo[:-2]))

    #网络请求
    def http_post(self,url):
        try:
            response  = requests.get(url, timeout = 5)
            res = {'code':'404','msg':'网络请求失败！','data':''}
            if response.status_code==200:
                res['code'] = '0000'
                res['msg']  = '请求成功！'
                res['data'] = response.text
                return res
            else:
                return res
        #没有网络或者请求超时依然返回,正常情况下也返回
        except:
            return {'code':'9999','msg':'网络错误！','data':''}


    #这个方法只会被执行一次   需要返回值
    def start(self,name):

    #插件等待（暂时停止）  唤醒触发
    def pause(self):

    #插件继续#二次开始start
    def resume(self, name):


    #插件结束
    def stop(self, *enobj):





