import requests,json,os
from package.include.model import model
from package.base import Base,log
#开发协议
#主类必须def __init__(self,x):
#调用方法必须def main(self,x):
#调用用户id是 self.uid  =  x.uid.value
#代码错误返回 return {'state':False,'data': "网络可能有问题",'msg':'',}
#不想继续调用录音  return {'state':True,'stop':True}


class My(Base):

    def __init__(self,x):
        self.uid = x.uid.value

    def main(self,x):
        if self.uid == 0:
            return {'state':True,'data': "不知道呢" ,'msg':'',}

        info = self.data.user_info( self.uid )
        name = info['nickname']
        return {'state':True,'data': "你是{0},已经记在了我的心里，忘不掉了。".format(name) ,'msg':'',}


