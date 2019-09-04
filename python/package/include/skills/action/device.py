from package.base import Base       #基本类
import package.mymqtt as mymqtt                         #mqtt服务（神经网络）
import package.include.skills.action.voices as voices
import package.include.skills.action.screens as screens
import os
class Device(Base):
    """设备技术类"""

    def __init__(self, public_obj):
        self.public_obj = public_obj
        self.Mqtt = mymqtt.Mymqtt(self.config)
    #设备信息
    def device_s(self, body):

        try:
            have_volume = voices.Voices(self.public_obj).chushizhi()
            have_screen = screens.Screen(self.public_obj).init_screen()
            if have_volume and have_screen:
                self.Mqtt.send_admin('xiaocx', 'DEVICE_STATE', { "code":"0000","info":{"screen":have_screen ,"sound": str(int(have_volume)) }})
                return {'state':True,'data': "微信小程序已连接",'msg':'','type':'system','stop':True}
            else:
                self.Mqtt.send_admin('xiaocx', 'DEVICE_STATE', { "code":"9999","info":{"screen":"屏幕初始化状态失败","sound":"获取当前设备音量失败"}})
                return {'state':True,'data': "微信小程序连接失败",'msg':'','type':'system','stop':True}
        except:
            #self.Mqtt.send_admin('xiaocx', 'DEVICE_STATE', { "code":"9999","info":{"screen":"屏幕初始化状态失败","sound":"获取当前设备音量失败"}})
            self.Mqtt.send_admin('xiaocx', 'DEVICE_STATE', { "code":"0000","info":{"screen":'1' ,"sound": "60"  }})
            return {'state':True,'data': "微信小程序连接失效",'msg':'','type':'system','stop':True}

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
        try:

            have = name['data']["value"]
            if have == "0" or have == 0:
                if  screens.Screen(self.public_obj).main("off") :
                    self.Mqtt.send_admin('xiaocx', 'DEVICE_SCREEN',{"code":"0000","msg":"屏幕关闭"})
                    return {'state':True,'data': "屏幕已经关闭",'msg':'','type':'system','stop':True}
                else:
                    self.Mqtt.send_admin('xiaocx', 'DEVICE_SCREEN',{"code":"9999","msg":"关闭屏幕失败"})
                    return {'state':True,'data': "关闭屏幕失败",'msg':'','type':'system','stop':True}

            elif have == "1" or have == 1:
                if have == screens.Screen(self.public_obj).main("on"):
                    self.Mqtt.send_admin('xiaocx', 'DEVICE_SCREEN',{"code":"0000","msg":"屏幕打开"})
                    return {'state':True,'data': "屏幕已经打开",'msg':'','type':'system','stop':True}
                else:
                    self.Mqtt.send_admin('xiaocx', 'DEVICE_SCREEN',{"code":"9999","msg":"打开屏幕失败"})
                    return {'state':True,'data': "打开屏幕失败",'msg':'','type':'system','stop':True}

            else:
                self.Mqtt.send_admin('xiaocx', 'DEVICE_SCREEN',{"code":"9999","msg":"操作屏幕失败"})
                return {'state':True,'data': "屏幕操作失败",'msg':'','type':'system','stop':True}
        except:
            self.Mqtt.send_admin('xiaocx', 'DEVICE_SCREEN',{"code":"9999","msg":"操作屏幕失败"})
            return {'state':True,'data': "屏幕操作失败",'msg':'','type':'system','stop':True}


if __name__ == '__main__':
    exit()
    Device().device_volume( {'data':{'value':40}} )