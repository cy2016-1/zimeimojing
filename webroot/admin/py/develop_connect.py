import json
from python.bin.Device import Device
from .Base import Base

class develop_connect(Base):
    '''设备初始化连接类'''

    def __init__(self, handler):
        super().__init__(handler)

    # 用于手动添加设备验证（明文验证）
    def verification(self):
        ret_arr = {'code' : '9999','message': '未知错误','data': ''}
        username = self._POST['username']
        password = self._POST['password']

        if len(username)<=0 or len(password)<=0:
            ret_arr['code'] = '1001'
            ret_arr['message'] = '登录账号或密码不能为空'
            return json.dumps(ret_arr)

        data = {'username': username,'password': password}
        (vst, md5pass) = self.verifuserpass(data)

        if vst is True:
            deviceid = Device.deviceid()
            ret_arr['code'] = '0000'
            ret_arr['message'] = '服务器验证成功'
            ret_arr['data'] = {'deviceid':deviceid, 'user': username,'pass': md5pass}
        else:
            ret_arr['code'] = '1002'
            ret_arr['message'] = '账号或密码错误'
            ret_arr['data'] = md5pass

        return json.dumps(ret_arr)

    # 用于连接前验证（密文验证）
    def connverif(self):
        ret_arr = {'code' : '9999','message': '未知错误','data': ''}
        username = self._GET['username']
        password = self._GET['password']
        data = {'username': username,'password': password}
        vst = self.authorized(data)

        if vst is True:
            ret_arr['code'] = '0000'
            ret_arr['message'] = '服务器验证成功'
        else:
            ret_arr['code'] = '1003'
            ret_arr['message'] = '账号或密码错误'

        return json.dumps(ret_arr)

    # 反馈给扫描程序
    def scanserver(self):
        ret_arr = {'code' : '9999','message': '未知错误','data': ''}
        localver = Device.getlocalver()
        if localver:
            ret_arr['code'] = '0000'
            ret_arr['message'] = '验证成功'
            ret_arr['data'] = {'version': localver}
        else:
            ret_arr['code'] = '1004'
            ret_arr['message'] = '验证失败'
        return json.dumps(ret_arr)

    def main(self):
        op = self._GET['op']
        ret_arr = {'code' : '9999','message': '错误的参数！','data': ''}
        if op == 'verif':
            return self.verification()

        elif op == 'connverif':
            return self.connverif()

        elif op == 'scanserver':
            return self.scanserver()

        else:
            return json.dumps(ret_arr)
