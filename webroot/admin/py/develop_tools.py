import json
import os
import sys
from urllib.parse import unquote_plus

from WebServer import RequestInit
from python.package.Mylib import Mylib
from python.bin.Device import Device

class develop_tools(RequestInit):
    '''开发者工具'''

    # 消息调试
    def debug_message(self, data):
        try:
            json_data = json.loads(data)
            self.send( json_data )
        except:pass

        return data

    def load_pluginlist(self):
        self.pluginpath = r'./plugin'

        ret_arr = {'code' : '9999', 'message': '获取插件列表失败', 'data': ''}

        pluginlist = {}
        for filedir in os.listdir(self.pluginpath):
            if os.path.isdir(os.path.join(self.pluginpath, filedir)) and filedir != '__pycache__':

                json_file = os.path.join(self.pluginpath, filedir, 'config.json')
                if not os.path.isfile(json_file):
                    continue
                with open(json_file, 'r') as f:
                    config_json = json.load(f)
                    pluginlist[config_json['name']] = {'text': config_json['displayName']}

        if len(pluginlist) > 0:
            ret_arr['code']    = '0000'
            ret_arr['message'] = '获取插件列表成功！'
            ret_arr['data'] = {
                'type': 'select',
                'list': pluginlist
            }

        return json.dumps(ret_arr)


    def main(self):
        op = self._GET['op']
        message = '错误的参数或操作！'
        code = '9999'
        data = ''

        # 消息调试
        if op == 'debugmess':
            data = self._POST['data']
            data = unquote_plus(data,'utf-8')
            return self.debug_message(data)

        if op == 'Ajax_plugin':
            return self.load_pluginlist()

        ret_arr = {'code' : code, 'message': message, 'data': data}
        return json.dumps(ret_arr)

