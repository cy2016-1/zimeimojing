# -*- coding: utf-8 -*-
import os,random
from package.base import Base,log

import package.include.luyin as luyin                   #录音
import package.include.bofang as bofang                 #播放
import package.include.baiduapi.hecheng as hecheng      #百度语音合成（文字转语音）
import package.include.baiduapi.shibie as shibie        #百度识别

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

        print("已经初始化")

    #全部转换成功执行（已在main函数中被重写）
    def success(self, json ):
        pass

    #录音成功 -> 进入百度识别
    def luyin_success(self,results):
        json = shibie.Shibie().main(results)
        if json['state']==True:
            self.success( json )
        else:
            self.success({'state': False,'data': '我没听清你说了啥','type':'system','msg': '识别失败！'})

    #录音失败 -> 递归自己，继续调用自己工作
    def luyin_error(self,bug):
        log.info('出错继续录音',bug)
        self.luyin.main(5, self.parent_self)

    '''
    语音录音主函数
    参数：
        hx_chenggong  -- 内存共享变量
        is_one      -- 是否为首次唤醒
        command_execution   --  语音全部操作成功
        parent_self -- 主进程对象
    '''
    def main(self,hx_chenggong, is_one, command_execution, parent_self ):

        hx_chenggong.value = os.getpid()       #记录唤醒进程ID

        self.success = command_execution

        self.parent_self = parent_self

        self.yuyin_path = parent_self.yuyin_path

       # self.luyin_temp_file = os.path.join(self.yuyin_path,"audio.wav")         #录音临时保存文件

        parent_self.sw.init()   #初始化内部通讯

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
            parent_self.sw.send_info( send_txt )
            os.system(play_cmd)

            del send_txt,play_cmd,wozai,filearr

        self.luyin.main(5, parent_self )


