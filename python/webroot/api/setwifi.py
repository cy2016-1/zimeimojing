import json
import sys,os
from .ApiBase import ApiBase
from bin.Setnet import Wificore

class setwifi(ApiBase):

    # 设置WiFi配网信息
    def set_wifi_info(self, data):
        set_json = {}
        if len(data) > 1:
            set_json['wifiname'] = data['wifiname']
            set_json['wifipass'] = data['wifipass']
            set_json['scanssid'] = data['scanssid']

            #初始化网络状态
            Wificore().config_wifi(set_json)

            ret_str = {"code":"0000","msg":"正在验证网络"}
        else:
            ret_str = {"code":"9999","msg":"数据格式错误"}

        return json.dumps(ret_str)

    # 获取设备ID信息
    def get_equipm_id(self):
        ret_str = {"code":"0000", "data": self.config['MQTT']['clientid'], "msg":"获取设备ID信息成功"}
        return json.dumps(ret_str)

    def main(self):
        # sys.stderr = open(os.devnull, 'w')
        ret_str = {"code":"9999","msg":"数据格式错误"}
        if 'op' in dict(self.query).keys():
            op = self.query['op']
            if op == 'setinfo':
                return self.set_wifi_info(self.query)

            if op == 'getinfo':
                return self.get_equipm_id()

        return json.dumps(ret_str)
