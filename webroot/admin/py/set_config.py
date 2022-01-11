import json
import os
from urllib.parse import unquote_plus
from WebServer import RequestInit
from python.package.Mylib import Mylib

# 设置所有配置
class set_config(RequestInit):

    def main(self):
        # 获取配置
        if self._GET['op'] == 'getconfig':
            config_set = os.path.abspath('./data/conf/config_set.yaml')
            conf_set = Mylib.yamlLoad(config_set)
            config = Mylib.getConfig()  # 取全局配置
            ret_arr = {
                'code' : '0000',
                'message': '获取配置数据成功',
                'data': {
                    'config': config,
                    'setconfig': conf_set
                }
            }
            return json.dumps(ret_arr)

        elif self._GET['op'] == 'setconfig':
            data = self._POST['data']
            data = unquote_plus(data,'utf-8')

            ret_arr = {
                'code' : '9999',
                'message':'未知错误',
                'data':''
            }

            try:
                data = json.loads(data)
                conf_set = Mylib.getConfig()
                conf_set.update(data)
                Mylib.saveConfig(conf_set)
                ret_arr = {
                    'code' : '0000',
                    'message': '保存配置成功，您需要重启后生效！'
                }
            except:
                pass

            return json.dumps(ret_arr)


