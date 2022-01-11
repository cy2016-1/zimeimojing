import json
import sys
import os

from WebServer import RequestInit
from python.package.Mylib import Mylib
from python.module.WebApi.hefeng import hefeng

class desktop_mojing(RequestInit):

    def __init__(self, handler):
        super().__init__(handler)
        self.config = Mylib.getConfig()

    def main(self):
        # 获取配置
        op = self._GET['op']

        if op == 'getconfig':
            return json.dumps(self.config)

        # 获取天气数据
        elif op == 'getweather':
            city_json = self.config['LOCATION']
            hf = hefeng().getweather(city_json['city_cnid'], city_json['city'])
            return hf

        # 获取老黄历
        elif op == 'laohuangli':
            url = self.config['httpapi'] + '/raspberry/laohuangli.html'
            ret = Mylib.http_get(url)
            return ret['data']

        else:
            return '{"error":"lack of parameter"}'
