import json
import os
import copy
from urllib.parse import quote,unquote

from WebServer import RequestInit
from python.package.Mylib import Mylib

class plugin_list(RequestInit):

    def __init__(self, handler):
        super().__init__(handler)

        self.pluginpath = os.path.join( handler.System_Root, r'./plugin')

        self.config = Mylib.getConfig()  # 取全局配置

        self.plugintemp = {}
        template_path = os.path.join( handler.System_Root, r'data/conf/pluginconfig.json' )
        with open(template_path) as f:
            self.plugintemp = json.load(f)


    # 加载本地插件列表
    def __load_local_pugin(self):
        pluginlist = []

        for filedir in os.listdir(self.pluginpath):
            if os.path.isdir(os.path.join(self.pluginpath, filedir)) and filedir != '__pycache__':
                template_json = copy.deepcopy(self.plugintemp)          # 拷贝一个对象

                json_file = os.path.join(self.pluginpath, filedir, 'config.json')
                if not os.path.isfile(json_file):
                    continue
                with open(json_file, 'r') as f:
                    config_json = json.load(f)
                    template_json.update(config_json)
                    pluginlist.append(template_json)

        return pluginlist

    # 加载远程插件列表
    def __load_origin_plugin(self):
        url = self.config['httpapi'] + '/raspberry/pluginlist.html'
        ret = Mylib.http_get(url)
        origin_plugin = json.loads(ret['data'])
        return origin_plugin

    # 获取远程单个插件信息
    def __load_origin_plugin_info(self, pluginName):
        url = self.config['httpapi'] + '/raspberry/plugininfo.html'
        ret = Mylib.http_get(url,{'name':pluginName})
        plugininfo = {}
        try:
            plugininfo = json.loads(ret['data'])
        except:
            pass

        return plugininfo

    # 加载远程单个插件更新列表
    def __load_origin_plugin_uplist(self, pluginName, UserId):
        url = self.config['httpapi'] + '/raspberry/pluginuplist.html'
        postjson = {
            'pluginname': pluginName,
            'userid': UserId
        }
        ret = Mylib.http_post(url, postjson)
        origin_plugin = {}
        try:
            origin_plugin = json.loads(ret['data'])
        except:
            pass

        return origin_plugin

    # 加载插件列表
    def load_plugin_list(self):
        plugin_list = self.__load_local_pugin()
        ret_arr = {
            'code' : '0000',
            'message': '获取数据成功',
            'data': plugin_list
        }
        return json.dumps(ret_arr)

    # 获取本地单个插件信息
    def load_plugin_info(self, pluginName='' ):
        filedir = pluginName + '/'
        config_json = copy.deepcopy(self.plugintemp)
        json_file = os.path.join(self.pluginpath, filedir, 'config.json')
        file_json = {}
        if os.path.isfile(json_file):
            with open(json_file, 'r') as f:
                file_json = json.load(f)

        config_json.update(file_json)

        origin_info = self.__load_origin_plugin_info(pluginName)

        if len(origin_info)<=0:
            config_json['isRelease'] = 0            # 插件未发布
        else:
            config_json['isRelease'] = 1            # 插件已发布
            if not origin_info['webuid']:
                config_json['developid'] = 0        # 未知发布者
            else:
                config_json['developid'] = origin_info['webuid']

            config_json['isUpdate'] = 0
            if int(origin_info['stauts']) > 0:
                config_json['origin_version'] = 'V'+ origin_info['version']       # 远程版本号
                if Mylib.versionCompare(config_json['version'], origin_info['version']) > 0:
                    config_json['isUpdate'] = 1
            else:
                config_json['origin_version'] = '此插件发布审核中'

        ret_arr = {
            'code' : '0000',
            'message': '获取[%s]插件数据成功' % pluginName,
            'data': config_json
        }

        return json.dumps(ret_arr)

    # 单个插件的更新列表
    def load_plugin_uplist(self, pluginName, UserId):
        plugin_list = self.__load_origin_plugin_uplist(pluginName, UserId)
        ret_arr = {
            'code' : '0000',
            'message': '获取数据成功',
            'data': plugin_list
        }
        return json.dumps(ret_arr)

    # 更新插件配置信息
    def set_plugin_config(self, pluginName, updata):
        filedir = pluginName + '/'
        json_file = os.path.join(self.pluginpath, filedir, 'config.json')

        ret_arr = {
            'code' : '1001',
            'message': '更新插件配置失败',
            'data': ''
        }

        try:
            config_json = {}
            with open(json_file, 'r') as f:
                config_json = json.load(f)

            config_json.update( updata )

            fw = open(json_file,'w',encoding='utf-8')
            json.dump(config_json, fw, ensure_ascii=False, indent=4)
            fw.close()
            ret_arr = {
                'code' : '0000',
                'message': '更新插件配置成功',
                'data': ''
            }
        except:pass

        return json.dumps(ret_arr)

    # 获取远程插件列表
    def load_allpugin(self):
        # 远程插件列表
        origin_plugin = self.__load_origin_plugin()

        # 本地已装插件
        local_plugin = self.__load_local_pugin()

        new_json = []
        for origin_item in origin_plugin:
            origin_item['state'] = '一键安装'
            for local_item in local_plugin:
                if origin_item['name']==local_item['name']:
                    origin_item['state'] = '已安装'
                    if Mylib.versionCompare(local_item['version'], origin_item['version']) > 0:
                        origin_item['state'] = '一键升级'
            new_json.append( origin_item )

        ret_arr = {
            'code' : '0000',
            'message':'获取全部插件数据成功',
            'data':new_json
        }
        return json.dumps(ret_arr)


    def main(self):

        # 本地安装的插件列表
        if self._GET['op']=='getlist':
            return self.load_plugin_list()

        # 官方全部插件列表
        if self._GET['op']=='getalllist':
            return self.load_allpugin()

        # 单个插件信息
        if self._GET['op']=='getinfo':
            name = self._GET['name']
            return self.load_plugin_info( name )

        # 单个插件升级更新信息
        if self._GET['op']=='getupinfo':
            name = self._POST['name']       # 插件名称
            userid = self._POST['userid']     # 用户ID
            return self.load_plugin_uplist(name, userid)

        # 更新插件配置信息
        if self._GET['op']=='setconfig':
            data = self._POST['data']
            data = unquote(data,'utf-8')

            ret_arr = {
                'code' : '9999',
                'message':'未知错误',
                'data':''
            }

            try:
                data_json = json.loads(data)
                if 'pluginName' in data_json:
                    pluginName = data_json['pluginName']
                    if pluginName is not None:
                        del data_json['pluginName']
                        return self.set_plugin_config(pluginName, data_json)
            except:
                pass
            return json.dumps(ret_arr)


