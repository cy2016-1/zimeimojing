#基本类
from package.base import Base
from urllib.request import urlopen,Request
from urllib.parse import urlencode
import json,re
from plugin import Plugin
import run as run
class Weatheraddress( Plugin,Base ):

    def http_urllib(self,postdata):


        try:

            res  = {'code':'9999','msg':'请求失败！','data':''}
            url  = "https://search.heweather.net/find?"
            data = urlencode({'location': postdata, 'key': 'ba623341728e4c08af816220f07821c1'})
            req  = Request(url, data.encode('utf-8'))
            f    = urlopen(req,timeout = 10)

            if f.getcode() == 200:
                response  =   json.loads( f.read().decode() )
                res['code'] = '0000'
                res['msg']  = '请求成功！'
                res['data']  = response["HeWeather6"][0]

        finally:
            return res

    def start(self,data):
        #获取触发词后面的索引位置
        path = re.search(data["trigger"], data["data"]).span()[-1]
        #检测用户输入的是否只是触发词
        if data["data"][path:]=="。" or len(data["data"][path:]) < 2:
            return {'state':True,'data': "设置天气为什么地方？。" ,'msg':''}
        #等到触发词+点符号后面的关键词,去除语句最后的符号
        if data["data"][path+1]=="。" or data["data"][path+1]==",":
            http_data = data["data"][path+1:-1]
        else:
            http_data = data["data"][path:-1]
        #请求服务器
        have = self.http_urllib(http_data)

        print(have["data"])
        print(have["data"]['basic'][0]["cid"])
        #判断网络是否正常和服务器返回是否正常
        if have["code"]=="0000" and have["data"]["status"] =="ok" and len(have["data"]['basic'][0]["location"]) <=10:
            #修改数据库
            self.data.up_config({"key":"city_cnid",'value':have["data"]['basic'][0]["cid"]})
            #返回结果
            run.stop("moJing")
            return {'state':True,'data': "设置天气为{}重启生效。".format(http_data) ,'msg':'','stop':True}

        else:
            #错误也返回结果
            return {'state':True,'data': "设置天气失败，可能语句缺少省市单位" ,'msg':'','stop':True}
if __name__ == '__main__':

    print(Weather_address().start({"data":"天津"}))














