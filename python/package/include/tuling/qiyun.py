# -*- coding: utf-8 -*-
from package.base import Base,log
import urllib.request,re,json,string


class Tuling(Base):

    def __init__(self):

        self.apiUrl  = self.config["QINYUIN"]["url"]

    '''main# 对外调用接口
    参数：
        name:需要输入图灵交流的文字。字符串类型'
    返回：
        正常:返回图灵的对话  类型：字符串
        网络异常:返回No_network#没有网络   类型：字符串
        异常：返回你传入的参数类型错误  类型：字符串
    '''
    def main(self,name):
        try:
            if self.mylib.typeof(name) != 'str':
                return {'state':False,'data': '我不知道你说了啥','type':'system', 'msg':'参数1，需要输入图灵交流的文字。字符串类型！'}

            tmp = self.apiUrl + name
            #转码
            url = urllib.parse.quote(tmp, safe=string.printable)
            #响应时间定为了25秒是应为该服务器不是那么快
            page = urllib.request.urlopen(url,timeout = 25)
            #判断网络请求成功
            if page.getcode() == 200:
                html = page.read().decode("utf-8")
                #判断返回数据是否是字典,可能返回的是数字所以str
                if re.sub( r'{.*}', "", str(html)) == "":
                    res = json.loads(html)
                    #删除字典内容和网址
                    data = re.sub(r'{.*}|网址.*', "", res['content'])
                    if data == '': data = "不知道"
                    del res,page,tmp,url,html
                    return {'state':True,'data':data ,'type':'tuling','msg':'图灵回复成功！'}
                else:
                    return {'state':False,'data':'我想不出来。','type':'system','msg':'服务器返回的不是字典！'}
            else:
                return {'state':False,'data':'网络可能有点问题，请检查一下网络哦。','type':'system','msg':'请求失败！'}
        except Exception as bug:
            log.warning('图灵超时',bug)
            return {'state':False,'data':'网络可能有点问题，需要检查一下网络。','type':'system','msg':'连接图灵服务器超时！'}

if __name__ == '__main__':


    print( Tuling().main('520'))