import json
import os
import copy

from .ApiBase import ApiBase
from package.mylib import mylib

class plugin_custom(ApiBase):
    '''插件自定义配置'''

    def __init__(self, handler):
        super().__init__(handler)

        self.pluginpath = r'./plugin'
        self.plugintemp = {}
        template_path = r'./data/conf/pluginconfig.json'
        with open(template_path) as f:
            self.plugintemp = json.load(f)

    def get_plugin_custom(self, pluginNmae):
        filedir = pluginNmae + '/'
        config_json = copy.deepcopy(self.plugintemp)
        json_file = os.path.join(self.pluginpath, filedir, 'config.json')
        config_api = ''
        if os.path.isfile(json_file):
            file_json = {}
            with open(json_file, 'r') as f:
                file_json = json.load(f)

            config_json.update(file_json)
            if config_json['webAdminApi'] != '':
                config_api = os.path.join('/plugin/'+ filedir + config_json['webAdminApi'])
        return config_api

    def main(self):
        ret_arr = {
            'code' : 20000,
            'message':'获取全部插件数据成功',
            'data': ""
        }
        if self.query['op']=='getconfigapi':
            pluginName = self.query['name']
            config_api = self.get_plugin_custom(pluginName)
            ret_arr['data'] = config_api
        return json.dumps(ret_arr)