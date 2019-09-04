# encoding:utf-8
#import urllib2
import json,base64,os,requests
import urllib.request
from package.base import Base,log
import package.include.baiduapi.token as key

class Contrast_face(Base):
    '''视觉-人脸对比类'''

    def __init__(self):
        self.token_file  = os.path.join(self.config["root_path"],'data/shijue/token.txt')
        self.huoqu_token = key.Token(self.token_file)
        log.info("在线人脸对比初始化完成")

    def success(self,jieguo):
        log.info(jieguo)

    def error(self,bug='bug'):
        log.info(bug)

    '''
    * 开始人脸对比
    * sou_name  -   源图片
    * new_name  -   对比图片
    '''
    def main(self, sou_name, new_name):
        datas = self.huoqu_token.main()
        if datas['state']:

            request_url = self.config['BAIDUAPI']['url']['duibi_api_url'] + "?access_token=" + datas['access_token']
        else:
            return 0
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


