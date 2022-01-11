import json
import os
import sys
import psutil
import re

from WebServer import RequestInit

class linux_network(RequestInit):
    '''树莓派系统 网络配置'''

    # 获取网络配置
    def getnetwork(self):
        try:
            info = psutil.net_if_addrs()
            netcard_info = {}

            for k,v in info.items():
                if k == 'lo': continue
                net_item = {}
                for item in v:
                    address = re.sub(r'\%'+str(k),'', str(item[1]))
                    if str(item[0]).strip() == 'AddressFamily.AF_INET':
                        net_item['IPv4'] = {
                            'address': address,
                            'netmask': item[2],
                            'broadcast': item[3]
                        }
                    if str(item[0]).strip() == 'AddressFamily.AF_INET6':
                        continue
                        # net_item['IPv6'] = {
                        #     'address': address,
                        #     'netmask': item[2],
                        #     'broadcast': item[3]
                        # }
                    if str(item[0]).strip() == 'AddressFamily.AF_PACKET':
                        net_item['MacAdd'] = {
                            'address': str(item[1]).upper()
                        }

                netcard_info[k] = net_item

            return netcard_info
        except:
            return {}


    def main(self):
        op = self._GET['op']
        message = '错误的参数或操作！'
        code = '9999'
        data = ''

        # 获取网络配置
        if op == 'getnetwork':
            info = self.getnetwork()
            if len(info) > 0:
                message = '获取网络配置成功'
                code = '0000'
                data = info
            else:
                message = '获取网络配置失败'
                code = '1001'

        ret_arr = {'code' : code, 'message': message, 'data': data}
        return json.dumps(ret_arr)
