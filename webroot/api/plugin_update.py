import json
import os
import re
import time
import requests

from .ApiBase import ApiBase
from python.package.Mylib import Mylib
from python.bin.Plugin import PluginRelease
from python.bin.Plugin import PlugUpdate

class plugin_update(ApiBase):

    PLUGIN_DIR = r'./plugin'

    # 获取单个插件信息（本地）
    def __load_pugin_info(self, pluginName='' ):
        filedir = pluginName + '/'
        json_file = os.path.join(self.PLUGIN_DIR, filedir, 'config.json')
        config_json = {}
        with open(json_file, 'r') as f:
            config_json = json.load(f)

        return config_json

    # 发布插件
    def release_pugin(self, pluginName, releasedata):

        ret = {'code': '9999','message': '未知错误！','data': ''}

        if not pluginName:
            ret['code'] = '1001'
            ret['message'] = '发布的插件名称不能为空。'
            return json.dumps(ret)

        if not releasedata['webuid']:
            ret['code'] = '1002'
            ret['message'] = '插件发布者不能为空。'
            return json.dumps(ret)

        if not releasedata['version']:
            ret['code'] = '1003'
            ret['message'] = '插件版本号不能为空。'
            return json.dumps(ret)

        if not re.search(r'^[v|V]?\d+\.\d+\.\d+$', releasedata['version'], re.M|re.I):
            ret['code'] = '1004'
            ret['message'] = '插件版本号必须为“x.x.x”格式。'
            return json.dumps(ret)

        # 加载插件原配置
        config_json = self.__load_pugin_info( pluginName )

        post_data = {
            'pluginName': pluginName,
            'webuid': releasedata['webuid'],
            'version': releasedata['version'],
            'explain': releasedata['explain'],
            'private': releasedata['private']
        }
        config_json.update(post_data)

        # 调用插件发布模块
        pr = PluginRelease(self.config)
        ret_json = pr.release(pluginName, config_json)

        return json.dumps(ret_json)

    # 升级插件
    def update_pugin(self, pluginName, version):
        config_json = self.__load_pugin_info( pluginName )

        PlugUp = PlugUpdate(self.config)
        return PlugUp.startUpdate(config_json)

    # 安装新插件
    def install_pugin(self, pluginName):
        PlugUp = PlugUpdate(self.config)
        return PlugUp.startInstall(pluginName)

    # 卸载插件
    def uninstall_pugin(self, pluginName):
        PlugUp = PlugUpdate(self.config)
        return PlugUp.startUninstall(pluginName)

    def main(self):
        op   = self.query['op']
        name = self.query['name']

        '''
        # 检测版本
        if op=='checkver':
            return self.checkver_pugin( name )
        '''

        # 升级插件
        if op=='update':
            version = self.query['version']
            return self.update_pugin(name, version)

        # 安装插件
        if op=='install':
            return self.install_pugin(name)

        # 卸载插件
        if op=='uninstall':
            return self.uninstall_pugin( name )

        # 发布插件
        if op=='release':
            version = self.query['version']     # 版本号
            explain = self.query['explain']     # 发布说明
            private = self.query['private']     # 私有插件
            webuid  = self.query['webuid']      # 发布人帐号ID
            post_data = {
                'version': version,
                'explain': explain,
                'private': private,
                'webuid': webuid
            }
            return self.release_pugin(name, post_data)
