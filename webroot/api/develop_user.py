import json
import os
import sys
import urllib

from .ApiBase import ApiBase
from python.package.Mylib import Mylib
from python.bin.Device import Device

class develop_user(ApiBase):
    '''开发者账号登录'''
    RECPATH = r"./runtime/info/developuser"

    # 获取本机IP地址
    def get_localhost(self):
        ipAddrs = os.popen("hostname -I").read()
        ipAddrs = ipAddrs.strip()
        ipAddrs = ipAddrs.split(' ')

        server_address = self.handler.server.server_address
        server_host = str(server_address[0])
        server_port = str(server_address[1])

        if server_host == '0.0.0.0':
            server_host = ipAddrs[0]

        return 'http://'+server_host+':'+ str(server_port)

    # 保存开发者账号到本地
    def saveaccount(self, userid, username):
        save_dict = {
            'userid': userid,
            'username': username
        }
        save_str = json.dumps(save_dict,ensure_ascii=False)
        encode_str = Device.develop_encode(save_str)

        temp_path  = os.path.dirname(self.RECPATH)
        if not os.path.isdir( temp_path ):
            try:
                os.makedirs( temp_path )     #创建保存目录
            except: pass
        del temp_path

        with open(self.RECPATH, 'w') as fso:
            fso.write(encode_str)

    # 获取开发者账号
    def getaccount(self):
        retstr = ''
        try:
            filestr = ''
            with open(self.RECPATH, 'r') as fso:
                filestr = fso.read()
            if len(filestr) > 0:
                filestr = Device.develop_decrypt(filestr)
                json.loads(filestr)     # 检测是否为正确的字典格式
                retstr = filestr
        except:
            pass
        return retstr

    # 退出开发者账号
    def exitaccount(self):
        try:
            with open(self.RECPATH, 'w') as fso:
                fso.write('')
            return True
        except:
            return False

    # 获取开发者账号详细信息
    def getaccountinfo(self, userid):
        dict_res = Device.develop_info(userid)
        ret_data = {}
        if dict_res['code'] == '0000':
            ret_data = dict_res['data']
        return ret_data

    # 获取开发者插件列表
    def getaccplugin(self, userid):
        dict_res = Device.develop_plugin(userid)
        return dict_res

    def main(self):
        op = self.query['op']
        message = '错误的参数或操作！'
        code = '9999'
        data = ''

        # 登录开发者账号
        if op == 'login':
            username = self.query['username']
            userpass = self.query['userpass']

            post_data = {
                'username': username,
                'userpass': userpass
            }
            message = '登录开发者账号失败，请检查账号和密码是否输入正确'
            code = '1001'

            url = self.config['httpapi'] + '/user/raspilogin.html'
            ret = Mylib.http_urllib(url, post_data)
            info = json.loads(ret['data'])
            if info['code'] == '0000':
                code = '0000'
                message = '登录开发者账号成功'
                data = {
                    'username': info['data']['username'],
                    'webuid': info['data']['webuid']
                }

        # 注册开发者账号
        elif op == 'regist':
            username = self.query['username']
            userpass = self.query['userpass']

            post_data = {
                'username': username,
                'userpass': userpass
            }
            message = '注册开发者账号失败，请检测注册信息是否输入正确'
            data = ''

            url = self.config['httpapi'] + '/user/raspiregist.html'
            ret = Mylib.http_urllib(url, post_data)
            info = json.loads(ret['data'])
            if info['code'] == '0000':
                message = '登录开发者账号注册成功'
                code = '0000'
                data = {
                    'username': info['data']['username'],
                    'webuid': info['data']['webuid']
                }
            else:
                message = info['msg']

        # 保存开发者账号
        elif op == 'saveaccount':
            webuid = self.query['webuid']
            username = urllib.parse.unquote(self.query['username'], encoding='utf-8')

            message = '保存开发者账号失败'
            self.saveaccount( webuid, username )        # 这里以后要加验证
            message = '保存开发者账号成功'
            code = '0000'

        # 获取开发者账号
        elif op == 'getaccount':
            message = '获取开发者账号失败'
            data = {}
            val = self.getaccount()

            if not val:
                message = '获取开发者账号失败'
                code = '1001'
            else:
                message = '获取开发者账号成功'
                code = '0000'
                data = val

        # 获取开发者账号详细信息
        elif op == 'getaccountinfo':
            userid = self.query['userid']
            message = '获取开发者账号失败'
            data = {}
            val = self.getaccountinfo(userid)

            if val is None:
                message = '获取开发者账号失败'
                code = '1001'
            else:
                message = '获取开发者账号成功'
                code = '0000'
                data = val

        elif op == 'getaccplugin':
            userid = self.query['userid']
            message = '获取开发者已发布插件列表失败'
            data = {}
            val = self.getaccplugin(userid)

            if val is None:
                message = '获取开发者已发布插件列表失败！'
                code = '1001'
            else:
                message = '获取开发者已发布插件列表成功！'
                code = '0000'
                data = val


        # 退出开发者账号
        elif op=='exitaccount':
            message = '退出开发者账号失败'
            data = {}
            code = '9999'
            st = self.exitaccount()
            if st==True:
                message = '退出开发者账号成功'
                code = '0000'
            else:
                code = '1001'

        ret_arr = {'code' : code, 'message': message, 'data': data}
        return json.dumps(ret_arr)

