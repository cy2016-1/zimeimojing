import json
import os
import sys
import re
import time

from WebServer import RequestInit
from python.package.Mylib import Mylib

class system_update(RequestInit):
    def __init__(self, handler):
        super().__init__(handler)
        self.zmprogress = '/tmp/zmprogress'


    def __get_local_ver(self):
        version = 'v0.0.1'
        with open('./data/ver.txt', 'r') as f:
            version = f.read()
        return version

    # 获取远程版本号
    def __get_remote_ver(self):
        gitee_url = 'https://gitee.com/kxdev/zimeimojing'
        new_upurl = gitee_url + '/raw/master/data/ver.txt'
        old_upurl = gitee_url + '/raw/master/python/data/ver.txt'

        version = '0.0.1'
        ret = Mylib.http_get(new_upurl, timeout=10)
        if ret['code'] != '0000':
            ret = Mylib.http_get(old_upurl, timeout=10)

        if ret['code']=='0000' and ret['data'] is not None:
            version  = ret['data']
        return version

    # 获取远程版本号
    def get_remote_ver(self):
        remote_ver = ''
        local_ver = ''
        code = '9999'
        message = '未能获取到'
        data = {'upgrade':0,'remotever':''}
        try:
            remote_ver = self.__get_remote_ver()
            local_ver  = self.__get_local_ver()

            if Mylib.versionCompare(local_ver, remote_ver)>0:
                data = {
                    'upgrade': 1,
                    'localver': local_ver,
                    'remotever':remote_ver
                }
                code = '0000'
                message = '官方最新版：'+ remote_ver +'，已经更新，可以升级'
            else:
                data = {
                    'upgrade': 0,
                    'localver': local_ver,
                    'remotever':remote_ver
                }
                code = '0000'
                message = '当前系统版本已经是最新的了，不需要升级'
        except:
            pass

        ret_arr = {'code': code,'message': message, 'data':data}
        return ret_arr

    # 获取本地版本号
    def get_localver(self):
        ret = {
            'code': '0000',
            'message': '获取当前系统版本号成功',
            'data': {
                'version': str(self.__get_local_ver())
            }
        }
        return ret

    # 开始升级操作
    def startupdate(self):
        system_dir = os.path.abspath(os.path.dirname('./'))
        os.system('sudo python3 '+ system_dir + '/update.py startupdate &')
        ret_arr = {'code': '0000','message': '提交升级操作成功！'}
        return ret_arr

    # 当前升级状态
    def updatestate(self):
        message = '未能获取到'
        data = ''
        code = '9999'

        data_state = ''
        if os.path.isfile(self.zmprogress):
            try:
                with open(self.zmprogress, 'r') as f:
                    data_state = f.read()
            except:
                pass

        if len(data_state) > 0:
            code = '0000'
            data = data_state
            message = '获取升级操作状态成功'
        else:
            data = 0

        ret_arr = {'code': code, 'message': message, 'data':data}
        return ret_arr

    def main(self):
        ret_str = {"code":"9999", "msg":"数据格式错误"}

        if 'op' in dict(self._GET).keys():
            op = self._GET['op']

            # 获取本地版本号
            if op == 'localver':
                ret_arr = self.get_localver()
                return json.dumps(ret_arr)

            # 获取远程版本号
            elif op == 'remotever':
                ret_arr = self.get_remote_ver()
                return json.dumps(ret_arr)

            # 开始升级
            elif op == 'startupdate':
                ret_arr = self.startupdate()
                return json.dumps(ret_arr)

            # 升级状态
            elif op == 'updatestate':
                ret_arr = self.updatestate()
                return json.dumps(ret_arr)

        return json.dumps(ret_str)
