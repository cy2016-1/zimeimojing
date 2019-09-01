# -*- coding: utf-8 -*-
import os,random,re
from package.base import Base,log

import package.include.luyin as luyin                   #录音
import package.include.bofang as bofang                 #播放
import package.include.baiduapi.hecheng as hecheng      #百度语音合成（文字转语音）
import package.include.baiduapi.shibie as shibie        #百度识别
#import package.include.noise as noise        #降噪

'''
语音类
实现：录音 -> 保存本地 -> 上传百度语音识别 -> 返回识别后文字
'''
class Hecheng_bofang(Base):

    def __init__(self, is_snowboy ):
        self.yuyin_path = os.path.join(self.config['root_path'], 'data/yuyin')
        self.is_snowboy = is_snowboy

        self.hecheng = hecheng.Hecheng()
        self.hecheng.success = self.success
        self.hecheng.error = self.error

        self.bofang = bofang.Bofang()


    def success(self,position):         #os.path.join(self.yuyin_path,"result.wav")
        chiproc = self.bofang.paly_wav( position )
        chiproc.wait()                  #等待播放结束
        if self.reobj["state"]==False or ('stop' in self.reobj):
            self.is_snowboy.value = 0       # 停止
        else:
            self.is_snowboy.value = 2       # 启动第二次唤醒状态

    def error(self,bug):
        self.bofang.paly_wav( os.path.join(self.yuyin_path, "meiyou_wangluo.wav") )

    def main(self, reobj ):
        self.reobj = reobj
        #合成语音并播放
        self.hecheng.main( reobj )


'''
录音+识别 类（实现：语音转文字）
'''
class Luyin_shibie(Base):

    def __init__(self):
        self.luyin = luyin.Luyin()
        self.luyin.success = self.luyin_success
        self.luyin.error = self.luyin_error
        self.timer = 5      #录音时长
        #self.noise = noise.Noise()
        #print("已经初始化")

    #全部转换成功执行（已在main函数中被重写）
    def success(self, json ):
        pass

    #录音成功 -> 进入百度识别
    def luyin_success(self,results):
        json = shibie.Shibie().main(results)
        #json = shibie.Shibie().main(self.noise.main(results))
        if json['state']==True:
            self.success( json )
        else:
            #err_tishi = ["我没听清你说了啥","哎呀，你刚刚说了什么？我没听清","您确认刚才是跟我再说话吗？"]
           # filearr = err_tishi[ random.randint(0,len(err_tishi)-1) ]
            self.success({'enter':'voice','state': False,'data': '','type':'system','msg': '识别失败！','body':{}})


    #录音失败 -> 递归自己，继续调用自己工作
    def luyin_error(self,bug):
        log.info('出错继续录音',bug)
        self.luyin.main(self.timer, self.pyaudio_obj)

    '''
    语音录音主函数
    参数：
        hx_chenggong  -- 内存共享变量
        is_one      -- 是否为首次唤醒
        command_execution   --  语音全部操作成功
        pyaudio_obj --  录音对象
        public_obj  --  全局类对象
    '''
    def main(self,hx_chenggong, is_one, command_execution, pyaudio_obj, public_obj ):

        hx_chenggong.value = os.getpid()       #记录唤醒进程ID

        self.success = command_execution

        self.pyaudio_obj = pyaudio_obj
        self.pyaudio_obj.sw = public_obj.sw

        self.yuyin_path = pyaudio_obj.yuyin_path

        #如果是首次唤醒：执行魔镜应答声
        if is_one == 1:
            wozai = [
            {'text':'嗯','wav': 'zaina2.wav'},
            {'text':'我在','wav': 'zaina3.wav'}
            ]
            filearr = wozai[ random.randint(0,len(wozai)-1) ]

            #播放唤醒提示声
            play_cmd = 'aplay '+ self.yuyin_path +'/{}'.format(filearr['wav'])

            send_txt = {'init':1, 'obj':'mojing','msg': filearr['text']}
            public_obj.sw.send_info( send_txt )
            os.system(play_cmd)

            del send_txt,play_cmd,wozai,filearr

        self.luyin.main(self.timer, pyaudio_obj )


