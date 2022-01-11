import copy
import json
import os
import time
import re
import random
from urllib.parse import unquote, unquote_plus

from python.package.Mylib import Mylib

from .Base import Base


class develop_editor(Base):
    ''' 开发环境初始化 '''

    def __init__(self, handler):
        super().__init__(handler)
        self.pluginpath = r'./plugin'

        self.plugintemp = {}
        template_path = os.path.join( handler.System_Root, r'data/conf/pluginconfig.json' )
        with open(template_path) as f:
            self.plugintemp = json.load(f)

    # 加载插件列表
    def LoadPluginList(self):
        pluginlist = []
        ret = {'code': '9999','msg': '未知错误'}

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

        ret['code'] = '0000'
        ret['msg']  = '加载插件列表成功！'
        ret['data'] = pluginlist

        return ret

    # 预创建新插件准备
    def create_prepare(self):
        ret = {'code': '9999','msg': '未知错误'}

        ordnum = 0
        for filedir in os.listdir(self.pluginpath):
            if os.path.isdir(os.path.join(self.pluginpath, filedir)) and filedir != '__pycache__':
                rest = re.search(r'Project_(\d+)$', filedir, re.M|re.I)
                if rest:
                    if int(rest.group(1)) > ordnum:
                        ordnum = int(rest.group(1))

        ordnum += 1
        ret['code'] = '0000'
        ret['msg']  = '准备创建新插件成功！'
        ret['data'] = {
            'name': 'Project_'+ str(ordnum),
            'displayName': '新项目_'+ str(ordnum)
        }
        return ret

    # 创建新插件
    def create_plugin(self):
        ret = {'code': '9999','msg': '未知错误'}
        name = self._POST['name']
        displayName = self._POST['displayName']
        displayName = unquote_plus(displayName,'utf-8')

        newplugin_path = os.path.join(self.pluginpath, name)
        if os.path.isdir(newplugin_path):
            ret['code'] = '1001'
            ret['msg']  = name+ '插件已经存在！'
            return ret

        os.mkdir(newplugin_path)

        # 随机一个插件触发词
        trigtemp = ''
        template_path = r'./data/conf/triggerwords.temp'
        with open(template_path) as f:
            trigtemp = f.read()

        trigtemp = re.sub(r'\r|\n', '', trigtemp, re.M|re.I)
        trigarr = trigtemp.split(',')
        trig_chi = random.sample(trigarr, 1)

        # 组合config.json文件
        template_json = copy.deepcopy(self.plugintemp)
        template_json['name'] = name
        template_json['triggerwords'] = trig_chi
        template_json['displayName'] = displayName
        template_json['description'] = displayName
        template_json['IsEnable'] = True

        # 插件Python文件模板
        pythontemp = ''
        template_path = r'./data/conf/pluginpython.py'
        with open(template_path) as f:
            pythontemp = f.read()

        pythontemp = pythontemp.format(name, displayName, str(trig_chi[0]))

        try:
            json_file = os.path.join(newplugin_path, 'config.json')
            fw = open(json_file, 'w', encoding='utf-8')
            json.dump(template_json, fw, ensure_ascii=False, indent=4)
            fw.close()

            save_python_file = os.path.join(newplugin_path, name + '.py')
            fw = open(save_python_file, 'w', encoding='utf-8')
            fw.write(pythontemp)
            fw.close()
            ret['code'] = '0000'
            ret['msg']  = '创建新插件'+ name+ '成功！'
        except:
            os.system('rm -rf '+ newplugin_path )
            ret['code'] = '1002'
            ret['msg']  = '创建插件'+ name+ '失败！'

        return ret


    # 获取插件信息
    def GetPluginInfo(self, pluginName, fileName):
        filedir = pluginName + '/'
        json_file = os.path.join(self.pluginpath, filedir, fileName)
        file_demo = ''
        if os.path.isfile(json_file):
            with open(json_file, 'r') as f:
                file_demo = f.read(-1)
        return file_demo

    # 保存插件信息
    def SavePluginInfo(self, pluginName):
        filedir = pluginName + '/'
        data = self._POST['data']
        data = unquote_plus(data,'utf-8')

        ret = {'code': '9999','msg': '未知错误'}

        if len(data) <= 0:
            return {'code': '1001','msg': '数据为空，无需保存！'}
        json_file = os.path.join(self.pluginpath, filedir, pluginName + '.py')

        if os.path.isfile(json_file):
            try:
                with open(json_file, 'w') as f:
                    f.write(data)
                ret['code'] = '0000'
                ret['msg']  = '保存文件成功！'
            except:
                ret['code'] = '1003'
                ret['msg']  = '保存文件失败！'
        else:
            ret['code'] = '1002'
            ret['msg']  = '保存文件失败，文件不存在！'

        return ret

    # 运行插件
    def runPlugin(self, pluginName):
        ret = {'code': '9999', 'msg': '未知原因导致发送运行指令失败！'}

        json_data = {"MsgType": "Stop", "Receiver": pluginName}
        self.send(json_data)
        time.sleep(0.5)

        json_data = {"MsgType": "LoadPlugin", "Receiver": "ControlCenter", "Data": pluginName}
        self.send( json_data )
        time.sleep(0.5)

        json_data = {"MsgType": "Start", "Receiver": pluginName}
        send_st = self.send(json_data)
        if send_st is None:
            ret['code'] = '0000'
            ret['msg']  = '发送运行插件指令成功！'
        else:
            ret['code'] = '1001'
            ret['msg']  = send_st
        return ret

    # 停止插件
    def stopPlugin(self, pluginName):
        json_data = {"MsgType": "Stop", "Receiver": pluginName}

        ret = {'code': '9999', 'msg': '未知原因导致发送失败！'}
        send_st = self.send(json_data)

        if send_st is None:
            ret['code'] = '0000'
            ret['msg']  = '停止插件消息发送成功'
        else:
            ret['code'] = '1001'
            ret['msg']  = send_st
        return ret

    def main(self):
        op = self._GET['op']

        # 获取单个插件信息
        if op == 'loadPluginList':
            rest = self.LoadPluginList()
            return json.dumps(rest)

        # 获取单个插件信息
        if op == 'getPluginInfo':
            pluginName = self._GET['pluginName']
            fileName   = self._GET['fileName']
            rest = self.GetPluginInfo(pluginName, fileName)
            return json.dumps(rest)

        # 保存单个插件
        if op == 'savePluginInfo':
            name = self._GET['name']
            rest = self.SavePluginInfo(name)
            return json.dumps(rest)

        # 运行单个插件
        if op == 'runPlugin':
            name = self._GET['name']
            rest = self.runPlugin(name)
            return json.dumps(rest)

        # 停止单个插件运行
        if op == 'stopPlugin':
            name = self._GET['name']
            rest = self.stopPlugin(name)
            return json.dumps(rest)

        # 创建新插件准备
        if op == 'createprepare':
            rest = self.create_prepare()
            return json.dumps(rest)

        # 创建新插件
        if op == 'createPlugin':
            rest = self.create_plugin()
            return json.dumps(rest)

        return json.dumps(op)
