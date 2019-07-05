# -*- coding: utf-8 -*-
from package.base import Base,log
import sys,os,json,base64,requests,urllib.request

#参考资料https://www.cnblogs.com/Pond-ZZC/p/6718205.html
#播放声音https://blog.csdn.net/xiongtiancheng/article/details/80577478

class Shibie(Base):
    '''百度语音识别'''

    def __init__(self):
        self.token_file = os.path.join(self.config['root_path'] , 'data/yuyin/baidu_token.txt')


    '''联网获取token
    返回：
        正常： 返回token
        网络异常;返回'No_network'
    '''
    def __lianwang_huoqutoken(self):
        log.info('正在网络请求：access_token')
        #获取token秘钥
        url  = self.config['BAIDUAPI']['url']['shibie_token_url']
        body = self.config['BAIDUAPI']['yuyin_body']

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
        jiancha = os.path.exists( self.token_file )#检查

        log.info('是否存在本地缓存access_token', jiancha)

        if jiancha == False:        #没有该文件的话，创建一下，并写入，在返回token
            token = self.__lianwang_huoqutoken()
            if token['state']==False:
                return token
            with open(self.token_file,'w',encoding='utf-8') as of:
                of.write(token['access_token'])         #初始化写入的是tokenk
                return {'state': True, 'access_token': token["access_token"], 'msg':'获取access_token成功'}

        else:       #如果有的话,过滤获取得到tokenk在返回
            log.info('正在读取本地缓存access_token')
            with open(self.token_file,encoding='utf-8') as of:
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



    '''（私有方法）__yuyin_shibie_api#   链接百度语音识别的api方法
    参数：
        audio_data :  二进制
    返回：
        正常:返回识别出的文字.  类型： 列表
        识别异常：返回 识别失败" 类型： 字符串
        网络异常:返回No_network#没有网络
    '''
    def __yuyin_shibie_api(self,audio_data):

        token = self.__huoqu_token()
        if token['state'] == False:
            return token

        speech_data = base64.b64encode(audio_data).decode("utf-8")
        #用Base64编码具有不可读性，需要解码后才能阅读
        speech_length = len(audio_data)
        post_data = {"format":"wav","rate": 16000,
        "channel": 1,"cuid":self.config['BAIDUAPI']['CUID'],
        "token": token['access_token'], "speech": speech_data,"len": speech_length}

        url = self.config['BAIDUAPI']['url']['shibie_api_url']
        json_data = json.dumps(post_data).encode("utf-8")
        json_length = len(json_data)

        try:
            req = urllib.request.Request(url,data=json_data)
            req.add_header("Content-Type", "application/json")
            req.add_header("Content-Length", json_length)
            resp = urllib.request.urlopen(req,timeout=20)##合成时间不多，识别最耗时
            resp = resp.read()
            resp_data = json.loads(resp.decode("utf-8"))

        except:
            log.warning('超时s2')
            return {'state': False,'data':'','msg':'百度语音识别失败，可能是网络超时。'}
            #return 'No_network'#没有网络

        if resp_data["err_no"] == 0:
            return {'state': True,'data':resp_data["result"][0],'msg':'识别成功！'}
            #return resp_data["result"]  #返回识别出的文字
        else:
            return {'state': False,'data':'','msg':'百度语音识别失败。'}
            #return "识别失败"

    '''zhixing# 对外调用接口
    参数：
        name: 声音文件 ,类型是wav
    返回：
        正常:返回识别出的文字  类型：字符串
        网络异常:返回No_network#没有网络   类型：字符串
    '''
    def main(self,audio_data):
     #   if self.mylib.typeof(name) !='str':
     #       resp = {'state': False,'data':'','msg':'参数1，需要输入被识别的录音的名字，str类型文件是WAV格式'}
     #       return resp
     #   if name[-4:] != '.wav':
     #       resp = {'state': False,'data':'','msg':'参数1，录音文件格式.wav'}
     #       return resp
        try:
           # f = open(name, "rb")
           # audio_data = f.read()
           # f.close()
            resp = self.__yuyin_shibie_api(audio_data)
            del audio_data
            log.info('识别结果',resp)
            if resp['state'] == False:
                return resp
            else:
                log.info(resp)
                return resp
        except :
            resp = {'state': False,'data':'','msg':'识别失败。'}
            return resp

if __name__ == '__main__':
    lei=Shibie()
    print(lei.main("data/yuyin/wo.wav"))