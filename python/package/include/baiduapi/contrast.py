# encoding:utf-8
#import urllib2
import json,base64,os,requests
import urllib.request
from package.base import Base,log

class Contrast_face(Base):
    '''视觉-人脸对比类'''

    def __init__(self):
        self.token_file  = os.path.join(self.config["root_path"],'data/shijue/token.txt')
        log.info("在线人脸对比初始化完成")


    def success(self,jieguo):
        log.info(jieguo)

    def error(self,bug='bug'):
        log.info(bug)

    '''（私有方法）__lianwang_huoqutoken#联网获取token
        返回：
            正常： 返回token
            网络异常;返回'No_network'
    '''
    def __lianwang_huoqutoken(self):
        #获取token秘钥
        url  = self.config['BAIDUAPI']['url']["duibi_token_url"]
        body = self.config['BAIDUAPI']['renlian_body']

        try:

            r = requests.post(url,data=body,verify=True,timeout=2)
            respond = json.loads(r.text)
            log.info(respond)
            return respond["access_token"]

        except:
            log.warning('超时s')
            return 'No_network'
            #在这里无论是没有网络还是获取token秘钥失败和异常都返回没有网络



    '''（私有方法）__huancun_token#缓存联网获取的token25天
        返回：
            正常： 返回token
            网络异常;返回'No_network'
    '''
    def __huancun_token(self):
        print( self.token_file )

        jiancha = os.path.exists(self.token_file)           # 检查
        log.info(jiancha)
        if jiancha == False: #没有该文件的话，创建一下，并写入，在返回token

            token=self.__lianwang_huoqutoken()
            if token =='No_network':
                return 'No_network'
            with open(self.token_file,'w',encoding='utf-8') as of:
                of.write(token)#初始化写入的是tokenk
                return token

        else:#如果有的话,过滤获取得到tokenk在返回
            log.info('正在读取缓存')
            with open(self.token_file,encoding='utf-8') as of:
                tokenk     = of.read()
                if tokenk != 'No_network':
                    return tokenk
                else:
                    return 'No_network'

    '''（私有方法）__huoqu_token #获取百度api的token的方法
        参数：
            无
        返回：
            正常：返回百度api的token
            异常：返回 No_network#没有网  类型;字符串
    '''
    def __huoqu_token(self):

        huancun=self.__huancun_token()
        if huancun =='No_network':
            return 'No_network'
        log.info('保存的缓存',huancun)
        if self.mylib.wenjian_guoqi(self.token_file)==True:
            log.warning('超过')
            return self.__lianwang_huoqutoken()                 #超过了25天就联网返回新token
        else:#
            log.info('缓存')
            return huancun

    '''
    * 开始人脸对比
    * sou_name  -   源图片
    * new_name  -   对比图片
    '''
    def main(self, sou_name, new_name):
        request_url = self.config['BAIDUAPI']['url']['duibi_api_url'] + "?access_token=" + self.__huoqu_token()

        with open(sou_name, 'rb') as f:
        # 参数images：图像base64编码
            img1 =base64.b64encode(f.read()).decode("utf-8")
        # 二进制方式打开图文件
        with open(new_name, 'rb') as f:
        # 参数images：图像base64编码
            img2 = base64.b64encode(f.read()).decode("utf-8")

        params = json.dumps(
            [{"image":str(img1), "image_type": "BASE64",
            "face_type": "LIVE", "quality_control": "LOW"},
             {"image":str(img2), "image_type": "BASE64",
              "face_type": "IDCARD", "quality_control": "LOW"}]).encode("utf-8")
        try:
            request = urllib.request.Request(url=request_url, data=params)
            request.add_header('Content-Type', 'application/json')      #表头
            response = urllib.request.urlopen(request,timeout=20)
        except:
            return 0
        try:
            content = response.read()
            content = bytes.decode(content) #去掉字典b头

            #log.info(json.loads(content))
            ##将字符串类型的字典转换为字典类型解析出来
            jieguo = json.loads(content)["result"]['score']
            #self.success(jieguo)
            return jieguo
        except:
            return 0






if __name__ == '__main__':

    Duibi().main()


