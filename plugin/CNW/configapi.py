import json
import os
from webroot.api.ApiBase import ApiBase

class configapi(ApiBase):

    this_path = os.path.dirname(__file__)

    # 加载系统配置
    def load_config_data(self):
        config_json = {}
        conf_file = os.path.join(self.this_path,'语音控制.json')
        with open(conf_file, 'r') as f:
            config_json['control'] = json.load(f)

        conf_file = os.path.join(self.this_path,'语音命令.json')
        with open(conf_file, 'r') as f:
            config_json['command'] = json.load(f)

        ret_arr = {
            'code' : 20000,
            'message':'获取全部数据成功',
            'data': config_json
        }
        return json.dumps(ret_arr)

    # 设置配置
    def set_config(self):
        settype = self.query['settype']
        setdata = self.query['data']
        setdata = json.loads(setdata)
        conf_file = ''
        if settype=='control':
            conf_file = '语音控制.json'
        elif settype=='command':
            conf_file = '语音命令.json'

        conf_file = os.path.join(self.this_path,conf_file)

        fw = open(conf_file,'w',encoding='utf-8')
        json.dump(setdata, fw, ensure_ascii=False, indent=4)
        fw.close()

        ret_arr = {
            'code' : 20000,
            'message':'设置语音配置成功！',
            'data':{
                'error': 0,
                'data': setdata
            }
        }
        return json.dumps(ret_arr)

    def main(self):
        ret_arr = {
            'code' : 20000,
            'message':'设置配置失败',
            'data': {
                'error': 9999,
            }
        }
        op = self.query['op']
        if op == 'getconfig':
            return self.load_config_data()

        if op == 'setconfig':
            return self.set_config()


        return json.dumps(ret_arr)