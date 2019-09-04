import requests,json,os
from package.include.model import model
from package.base import Base,log
#开发协议
#主类必须def __init__(self,x):
#调用方法必须def main(self,x):
#调用用户id是 self.uid  =  x.uid.value
#代码错误返回 return {'state':False,'data': "网络可能有问题",'msg':'',}
#不想继续调用录音  return {'state':True,'stop':True}



class Weather(Base):

    def __init__(self,x):
        self.db   = model(os.path.join(self.config['root_path'],"data/config.db"))
        #在数据库查找是否存在该语句对应指令
        where     =  {'key':"city"}
        self.name  =  self.db.table("config").where( where ).find()
        where     =  {'key':"city_cnid"}
        self.id_  =  self.db.table("config").where( where ).find()
        self.uid  =  x.uid.value
    def http_post(self):

        url="https://hapi.16302.com/raspberry/getweather.html"

        if not self.name or not self.id_ :
            return False
        try:
            self.name =  self.name[0]["value"]
            self.id_  =  self.id_[0]["value"]
            postdata={'cnid': self.id_, 'city': self.name}
            response  = requests.get(url, postdata,timeout=5 )#post

            if response.status_code==200:
                return json.loads(response.text)
            else:
                return "8888" #请求失败
        except:
            return "9999"#网络问题
    def main(self,x):

        data = self.http_post()
        if data:

            if data == "8888":
                return {'state':True,'data': "不知道了",'msg':'','stop':True}

            if data == "9999":
                return {'state':True,'data': "网络可能有问题",'msg':'','stop':True}

            if data["now"]["cond_txt"].count("雨") <1 :
              # print(data["now"])
                rain = "没有雨"
            else:
                rain = data["now"]["cond_txt"]

            if self.uid ==0:
                return {'state':True,'data': "{0}今天最高温度{1}摄氏度，{2}".format(self.name,data["now"]["tmp"],rain)    ,'msg':'',}
            else:
                info = self.data.user_info( self.uid )
                name = info['nickname']
                return {'state':True,'data': "你好{0},{1}今天最高温度{2}摄氏度，{3}".format(name,self.name,data["now"]["tmp"],rain)    ,'msg':'',}

        else:
            return {'state':True,'data': "缺少你的位置信息",'msg':'','stop':True}
if __name__ == '__main__':

    print(Weather().main())
