# -*- coding: utf-8 -*-
#IS_PY3 = sys.version_info.major == 3
#if IS_PY3:
import requests,os,sys,json,hashlib
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.parse import quote_plus
from package.base import Base,log

class Hecheng(Base):
    '''百度语音合成'''

    def __init__(self):
        # 发音人选择, 0为普通女声，1为普通男生，3为情感合成-度逍遥，4为情感合成-度丫丫，默认为普通女声
        self.PER = 4
        # 语速，取值0-15，默认为5中语速
        self.SPD = 5
        # 音调，取值0-15，默认为5中语调
        self.PIT = 5
        # 音量，取值0-9，默认为5中音量
        self.VOL = 5
        # 下载的文件格式, 3：mp3(default) 4： pcm-16k 5： pcm-8k 6. wav
        self.AUE = 6

        self.FORMATS = {3: "mp3", 4: "pcm", 5: "pcm", 6: "wav"}
        self.FORMAT  = self.FORMATS[self.AUE]
        self.CUID    = self.config['BAIDUAPI']['CUID']
        self.TTS_URL = self.config['BAIDUAPI']['url']['hecheng_api_url']

        self.token_file = os.path.join(self.config['root_path'], 'data/yuyin/baidu_token.txt')
        self.audio_file = os.path.join(self.config['root_path'], 'data/hecheng')


    '''（私有方法）__lianwang_huoqutoken#联网获取token
        返回：
            正常： 返回token
            网络异常;返回'No_network'
    '''
    def __lianwang_huoqutoken(self):
        #获取token秘钥
        url = self.config['BAIDUAPI']['url']['shibie_token_url']
        body =self.config['BAIDUAPI']['yuyin_body']

        try:
            r = requests.post(url,data=body,verify=True,timeout=2)
            respond = json.loads(r.text)
            return {'state': True, 'access_token': respond["access_token"], 'msg':'获取access_token成功'}
        except:
            return {'state': False,'access_token':'','msg':'网络连接超时'}
            #在这里无论是没有网络还是获取token秘钥失败和异常都返回没有网络



    '''（私有方法）__huancun_token#缓存联网获取的token25天
        返回：
            正常： 返回token
            网络异常;返回'No_network'
    '''
    def __huancun_token(self):

        jiancha = os.path.exists(self.token_file)#检查
        #log.info(jiancha)
        if jiancha == False: #没有该文件的话，创建一下，并写入，在返回token

            token=self.__lianwang_huoqutoken()
            if token =='No_network':
                return 'No_network'
            with open(self.token_file, 'w',encoding='utf-8') as of:
                of.write(token['access_token'])#初始化写入的是tokenk
                return {'state': True, 'access_token': token["access_token"], 'msg':'获取access_token成功'}

        else:#如果有的话,过滤获取得到tokenk在返回
            log.info('正在读取缓存')
            with open(self.token_file, encoding='utf-8') as of:
                f_token = of.read()
                return {'state': True, 'access_token': f_token, 'msg':'获取access_token成功'}

    '''（私有方法）__huoqu_token #获取百度api的token的方法
        参数：
            无
        返回：
            正常：返回百度api的token
            异常：返回 No_network#没有网  类型;字符串
    '''
    def __huoqu_token(self):
        huancun = self.__huancun_token()
        if huancun['state'] == False:
            return huancun
        if self.mylib.wenjian_guoqi(self.token_file)==True:
            log.warning('本地缓存已过期')
            #删除文件
            os.remove(self.token_file)
            return self.__lianwang_huoqutoken()#超过了25天就联网返回新token
        else:
            log.info('返回本地缓存')
            return huancun

    def success(self,position):
        pass
      #  log.info('合成正在调用播放！！！！！！！！！！！！！！！！！！')
        #self.bofang_leiduixiang.main("data/yuyin/result.wav")


    def error(self, bug ):
        pass

    '''zhixing# 对外调用接口
    参数：
        txt: 需要输入合成语音的文字。字符串类型
    返回：
        正常:在目录下合成一个声音  类型：wav文件
        网络异常:返回No_network#没有网络   类型：字符串
        异常：返回你传入的参数类型错误  类型：字符串
    '''
    def md5_(self,txt):
        m = hashlib.md5()
        m.update(txt.encode())
        return m.hexdigest()

    '''
    语音合成主函数
    reobj   --  传入参数 字典 类型
    '''
    def main(self,reobj):
        log.info('语音合成', reobj )

        re_type = reobj['type']       # system -- 系统回答，录音文件缓存，tuling -- 图灵机器不缓存
        re_text = reobj['data']

        #计算re_text字符串的md5
        md5 = self.md5_(re_text) + "." + self.FORMAT

        #在文件夹里查找.WAV文件
        audio_fill_ = os.path.join( self.audio_file , md5 )

        if os.path.isfile( audio_fill_ ):
            #log.info("本地声音文件存在.....")
            self.success( position = audio_fill_ )
            return True         #如果本地存在则不在执行下面代码

        try:
            if self.mylib.typeof(re_text) != 'str':
                return '参数1，需要输入合成语音的文字。字符串类型'

            token = self.__huoqu_token()
            if token['state'] == False:
                return token

            tex = quote_plus(re_text)  # 此处re_text需要两次urlencode
            params = {'tok': token['access_token'], 'tex': tex, 'per': self.PER, 'spd': self.SPD,
                'pit': self.PIT, 'vol': self.VOL, 'aue': self.AUE, 'cuid': self.CUID,
                'lan': 'zh', 'ctp': 1}  # lan ctp 固定参数
            data = urlencode(params)

           # log.info('Web浏览器测试' + self.TTS_URL + '?' + data)

            req = Request(self.TTS_URL, data.encode('utf-8'))
            del token,data

            try:
                f = urlopen(req,timeout=10)#合成时间不多，识别最耗时
                result_str = f.read()
                if re_type == 'system' :
                    save_file = audio_fill_
                else:
                    save_file = os.path.join(self.config['root_path'],'data/yuyin/','result.' + self.FORMAT )

                log.info('保存地址：', save_file )
                with open(save_file, 'wb') as of:
                    of.write(result_str)

                del result_str

                self.success(position=save_file)

            except Exception as bug:
                self.error(bug)
                return {'state': False,'data':'','msg':'可能是网络超时。'}

        except:
            return {'state': False,'data':'','msg':'可能是网络超时。'}




if __name__ == '__main__':
    lei=Hecheng()
    lei.main('测试魔镜')
