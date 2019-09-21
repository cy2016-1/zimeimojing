import os,re
from package.base import Base       #基本类
from plugin import Plugin
import package.mymqtt as mymqtt                         #mqtt服务（神经网络）
import plugin.temp.voices as voices
import plugin.temp.screens as screens

class Device(Base,Plugin):
    """设备技术类"""

    def __init__(self, public_obj):
        self.public_obj = public_obj
        self.Mqtt = mymqtt.Mymqtt(self.config)

    # 获取设备IP
    def get_ip_address(self):
        re_json = []
        
        restr = r'inet\s+([\d+\.]+)\s+'

        eth0ip = os.popen('ifconfig eth0').read()
        matc = re.search( restr, eth0ip, re.M|re.I )
        if matc!=None:
            ethjson = {
                'devname':'eth0',
                'name':'有线网卡',
                'ip': str(matc.group(1))
            }
            re_json.append( ethjson )

        wlanip = os.popen('ifconfig wlan0').read()
        matc = re.search( restr, wlanip, re.M|re.I )
        if matc!=None:
            ethjson = {
                'devname':'wlan0',
                'name':'无线网卡',
                'ip': str(matc.group(1))
            }
            re_json.append( ethjson )

        return re_json

    #设备信息
    def device_s(self, data):

        try:
            have_volume = voices.Voices(self.public_obj).chushizhi()

            #返回单个声音状态
            if data["data"]["state"] == "volume":
                self.Mqtt.send_admin('xiaocx', 'DEVICE_STATE', { "code":"0000","info":{"sound": str(int(have_volume))}})
                return {'state':True,'data': "",'msg':'','type':'system','stop':True}

            have_screen = screens.Screens(self.public_obj).init_screen()

            #返回单个屏幕状态
            if data["data"]["state"] == "screen":
                self.Mqtt.send_admin('xiaocx', 'DEVICE_STATE', { "code":"0000","info":{"screen":have_screen }})
                return {'state':True,'data': "",'msg':'','type':'system','stop':True}

            #获取全部状态
            if have_volume and have_screen and data["data"]["state"] == "all":
                # 设备IP信息
                dev_ip = self.get_ip_address()

                #天气预报默认城市信息
                data_config = self.data.getconfig()
                weathcity = {
                    'city': str(data_config['city']),
                    'city_cnid': str(data_config['city_cnid'])
                }

                body_json = {
                    "code":"0000",
                    "info":{
                        "screen":have_screen ,
                        "sound": str(int(have_volume)),
                        "devip": dev_ip,
                        "weathcity": weathcity
                    }
                }
                self.Mqtt.send_admin('xiaocx', 'DEVICE_STATE', body_json )

                return {'state':True,'data': "微信小程序已连接",'msg':'','type':'system','stop':True}
            else:
                self.Mqtt.send_admin('xiaocx', 'DEVICE_STATE', { "code":"9999","info":{"screen":"屏幕初始化状态失败","sound":"获取当前设备音量失败"}})
                return {'state':True,'data': "微信小程序获取设备信息失败。",'msg':'','type':'system','stop':True}
        except:

            self.Mqtt.send_admin('xiaocx', 'DEVICE_STATE', { "code":"0000","info":{"screen":'1' ,"sound": "60"  }})
            return {'state':True,'data': "微信小程序获取设备信息失败。",'msg':'','type':'system','stop':True}


    #设置音量
    def device_volume(self,name):
        try:
            set_value = str(name['data']['value'])
            have = voices.Voices(self.public_obj).main(set_value)
            if have:
                self.Mqtt.send_admin('xiaocx', 'DEVICE_VOLUME',{"code":"0000","msg":set_value })
                have['state'] = True
                have['stop'] = True
                return have
            else:
                self.Mqtt.send_admin('xiaocx', 'DEVICE_VOLUME',{"code":"9999","msg":"设置声音失败"})
                return {'state':True,'data': "设置声音失败",'msg':'','type':'system','stop':True}
        except:
            self.Mqtt.send_admin('xiaocx', 'DEVICE_VOLUME',{"code":"9999","msg":"设置声音失败"})
            return {'state':True,'data': "设置声音失效",'msg':'','type':'system','stop':True}

    # 旋转屏幕
    def device_rturn(self,name):
        self.Mqtt.send_admin('xiaocx', 'DEVICE_RTURN', { "code":"0000"})
        os.system("sudo python3 {0}".format(os.path.join(self.config['root_path'],"package/include/rotatingscreen.py")))

    #打开和关闭屏幕
    def device_screen(self,name):

        have = name['data']["value"]

        if have == "0" or have == 0:
            self.Mqtt.send_admin('xiaocx', 'DEVICE_SCREEN',{"code":"0000","msg":"屏幕关闭"})
            return screens.Screens(self.public_obj).main("off")

        elif have == "1" or have == 1:
            self.Mqtt.send_admin('xiaocx', 'DEVICE_SCREEN',{"code":"0000","msg":"屏幕打开"})
            return screens.Screens(self.public_obj).main("on")

        else:
            self.Mqtt.send_admin('xiaocx', 'DEVICE_SCREEN',{"code":"9999","msg":"操作屏幕失败"})
            return {'state':True,'data': "屏幕操作失败",'msg':'','type':'system','stop':True}

    #修改天气预报默认城市
    def device_city(self,name):
        data = name['data']
        if type(data) is dict:
            self.data.up_config({"key":"city_cnid",'value':data['cnid']})
            self.data.up_config({"key":"city",'value':data['name']})
            self.Mqtt.send_admin('xiaocx', 'DEVICE_CITY',{"code":"0000","msg":"修改天气预报默认城市成功"})
            self.public_obj.sw.send_nav({"event" : "close"})
            self.public_obj.sw.send_nav({"event" : "close"})
            return {'state':True,'data': "修改天气预报默认城市为"+ str(data['name']) ,'msg':'','type':'system','stop':True}
        else:
            self.Mqtt.send_admin('xiaocx', 'DEVICE_CITY',{"code":"1001","msg":"修改天气预报默认城市失败"})
            return {'state':True,'data': "修改天气预报默认城市失败",'msg':'','type':'system','stop':True}


    #入口
    def start(self,name):
        #print( name )
        #设置音量
        if name["action"]   == "DEVICE_VOLUME":
            return self.device_volume(name)

        #关闭屏幕
        elif name["action"] == "DEVICE_SCREEN":
            return self.device_screen(name)

        #旋转屏幕
        elif name["action"] == "DEVICE_RTURN":
            return self.device_rturn(name)

        #获取设备信息
        elif name["action"] == "DEVICE_STATE":
            return self.device_s(name)

        #修改天气预报默认城市
        elif name["action"] == "DEVICE_CITY":
            return self.device_city(name)



if __name__ == '__main__':
    pass