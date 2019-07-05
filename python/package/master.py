import pyaudio,time,webrtcvad,collections,sys,signal,wave,os,random
from array import array
from struct import pack
import multiprocessing as mp                            #多进程

from package.base import Base,log                       #基本类
import package.mysocket as mysocket                     #发送websocket
import package.include.snowboy.snowboy as snowboy       #语音唤醒
import package.include.yuyin as yuyin                   #语音相关操作（语音转文字：录音、识别）
import package.include.visual as visual                 #视觉相关（人脸识别）
import package.skills as skills                         #技能类（大脑）


'''初始化内部使用的对象（主要是传到语音相关进程中）'''
class import_obj(Base):

    def __init__(self):
        self.yuyin_path = os.path.join(self.config['root_path'], 'data/yuyin')
        self.time,self.collections,self.sys,self.signal,self.wave,self.array,self.pack,self.so = time,collections,sys,signal,wave,array,pack,os

        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        CHUNK_DURATION_MS = 30                              # supports 10, 20 and 30 (ms)
        PADDING_DURATION_MS = 1500                          # 1 sec jugement

        self.RATE = 16000
        self.CHUNK_SIZE = int(self.RATE * CHUNK_DURATION_MS / 1000)   # chunk to read
        self.NUM_PADDING_CHUNKS = int(PADDING_DURATION_MS / CHUNK_DURATION_MS)
        self.NUM_WINDOW_CHUNKS = int(400 / CHUNK_DURATION_MS)    # 400 ms/ 30ms  ge
        self.NUM_WINDOW_CHUNKS_END = self.NUM_WINDOW_CHUNKS * 2

        pa = pyaudio.PyAudio()
        self.stream = pa.open(format= FORMAT,
                    channels = CHANNELS,
                    rate = self.RATE,
                    input = True,
                    start = False,
                    # input_device_index=2,
                    frames_per_buffer = self.CHUNK_SIZE)

        #0: Normal，1：low Bitrate， 2：Aggressive；3：Very Aggressive
        self.vad = webrtcvad.Vad(3)

        self.sw = mysocket.Mysocket()


'''主控制类'''
class Master(Base):

    def __init__(self):
        #当前用户ID
        self.uid    = 0

        #初始化录音和识别
        self.Luyin_shibie =  yuyin.Luyin_shibie()

        #技能总控
        self.skills = skills.Skills()

        self.import_obj = import_obj()


    '''命令动作执行
    参数:
        sbobj -- 语音识别成功返回的字典对象
    '''
    def command_execution(self, sbobj ):
        log.info("进入主控：", sbobj )

        #语音识别成功
        if sbobj["state"]:

            #发送到前面屏幕
            send_txt = {'obj':'zhuren','msg': sbobj['data'] }
            self.import_obj.sw.send_info( send_txt )

            #从这里开始进入技能分析（得到最终返回文本）
            #=========================================================================
            reobj = self.skills.main( sbobj['data'] )
            #=========================================================================
            log.info('技能返回：', reobj )

        else:
            self.is_snowboy.value = 0
            reobj = sbobj

        #发送到前面屏幕
        send_txt = {'obj':'mojing','msg': reobj['data']}
        self.import_obj.sw.send_info( send_txt )

        #合成语音并播放
        yuyin.Hecheng_bofang(self.is_snowboy).main( reobj )


    ''''
    进入语音进程
    参数：
        is_one - 是否为首次唤醒 1- 首次 / 2 - 第二次（不在播放唤醒应答声）
    '''
    def enter_yuyin(self, is_one = 0):
        log.info("开始进入语音进程")
        if self.hx_yuyinpid.value > 0:
            os.system("sudo kill -9 {}".format(self.hx_yuyinpid.value))

        self.hx_yuyinpid.value = 0

        #启动新进程开始录音+识别
        self.p2 = mp.Process(
            target = self.Luyin_shibie.main,
            args = (self.hx_yuyinpid, is_one, self.command_execution, self.import_obj)
        )
        self.p2.start()


    #语音唤醒成功
    def snowboy_success(self):
        self.is_snowboy.value = 1

    #开始启动唤醒
    def start_snowboy(self):

        model  = os.path.join(self.config['root_path'],self.config['WAKEUP']['model'])      #语音唤醒模型
        sensit = self.config['WAKEUP']['sensit']

        resource = os.path.join(self.config['root_path'],'data/snowboy/common.res')

        #用新进程启动唤醒
        self.p1 = mp.Process(
            target = snowboy.Snowboy().main,
            args = (self.snowboy_success, model, sensit, resource )
        )
        self.p1.start()

    #人脸识别成功
    def face_success(self, uid):
        if uid > 0:
            log.info('已经认出是谁：', uid )
            info = self.data.user_info( uid )
            self.uid = info['uid']
            retxt = {'state':True,'data': '您好'+ info['nickname'] + '，很高兴为您服务！','type':'system', 'msg':''}
            yuyin.Hecheng_bofang(self.is_snowboy).main( retxt )

    #人脸识别
    def start_face(self):
        self.p3 = mp.Process(
            target = visual.Visual().main,
            args = (self.face_success,)
        )
        self.p3.start()

    #检测socket状态
    def detect_socket(self):
        print( self.import_obj.sw )
        try:
            self.import_obj.sw.send('{}')
        except Exception as e:
            self.import_obj.sw.reconnect()


    def main(self):

        #定义唤醒成功内存变量：记录语音进程ID
        self.hx_yuyinpid = mp.Value("h",0)

        #定义唤醒成功内存变量：是否唤醒成功
        self.is_snowboy  = mp.Value("h",0)

        #启动唤醒
        self.start_snowboy()

        is_face = os.path.join(self.config['root_path'],'data/is_face')

        #socket_timer = 0

        while True:
            #监听唤醒进程：是否正常
            if self.p1.is_alive()==False:
                self.start_snowboy()
                time.sleep(3)

            #监听语音唤醒：是否唤醒
            if self.is_snowboy.value > 0:
                self.enter_yuyin( self.is_snowboy.value )
                self.is_snowboy.value = 0

            #开始人脸识别
            if os.path.isfile(is_face) is False:
                self.start_face()
                os.mknod(is_face)       #创建空文件

            '''
            socket_timer += 1
            if socket_timer > 10:
                socket_timer = 0
                self.detect_socket()
            '''

            time.sleep(0.5)