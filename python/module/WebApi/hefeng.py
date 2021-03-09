import api.Weather.config as config
from package.mylib import mylib
import json,re
import requests

# 和风天气API接口
class hefeng():
    '''和风天气API接口'''
    def __init__(self):
        self.config = config.config()

    def webpost(self, api_url, location=''):
        apiurl = api_url + "?key="+ self.config['key'] +"&lang=zh&location=" + location
        ipstr = mylib.http_post(apiurl)
        return ipstr

    # ================================================================================
    def get_client_ip(self):
        response  = requests.get(url="http://hapi.16302.com/raspberry/get_client_ip.html",timeout=5)
        if response.status_code==200:
            data = response.text
            return data

        response  = requests.get(url="http://pv.sohu.com/cityjson",timeout=5)
        if response.status_code==200:
            data = response.text
            data = re.findall(r'({.*})', data)[0]
            data = json.loads(data)
            return data["cip"]
        return ''

    # get_city 获取当前网络IP和城市名称
    def get_city(self):
        ip = self.get_client_ip()
        api_url = 'https://geoapi.qweather.com/v2/city/lookup'
        ip_arr = self.webpost(api_url, ip)
        if ip_arr["code"]=="0000":
            data =  json.loads(ip_arr["data"])
            return data["location"][0]
        return {}

	# 根据城市名称获取城市ID信息
    def getcityid(self, cityname = ''):
        try:
            api_url = 'https://geoapi.qweather.com/v2/city/lookup'
            ip_arr = self.webpost(api_url, cityname)
            if ip_arr["code"]=="0000":
                data = json.loads(ip_arr["data"])
                return  data['location'][0]
        except:pass
        return {}

	# 获取天气预报数据
    def getweather(self, cnid='', city=''):
        if cnid == '':
            return ''
        api_url = "https://free-api.heweather.net/s6/weather"
        ip_arr = self.webpost(api_url, cnid)
        if ip_arr['code'] == '0000':
            json_arr = json.loads(ip_arr['data'])
            json_str = json.dumps(json_arr['HeWeather6'][0])
            return json_str
        return ''
