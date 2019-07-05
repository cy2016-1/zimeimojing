import hashlib                      #库模块md5加密算法
import json                         #库模块类型转换
import urllib,os
from package.base import Base       #基本类
class device(Base):
    """设备操作类"""

    # 获取设备ID
    def get_deviceid(self):
        mac = 'kycx'+ self.mylib.get_mac()
        deviceid = 'k'+hashlib.md5(mac.encode('utf-8')).hexdigest()[8:-14]
        return deviceid


    #设备上线
    def online(self):
        deviceid = self.get_deviceid()
        postdata = {'deviceid': deviceid,'version' : self.config['version']}
        url = self.config['httpapi'] + '/raspberry/online.html'

        http_res = self.mylib.http_post( url, postdata )
        if http_res['code'] == "9999":
            http_res = self.mylib.http_urllib( url, postdata )

        res = {'code':'9999','msg':'处理失败'}
        if (http_res['code']=='0000'):
            jsonstr = json.loads( http_res['data'] );
            res = http_res['data']
            #写数据库
            jsonstr['clientid'] = deviceid;
            self.data.save_necessary_data(jsonstr)                      # 保存必要数据到数据库
        return res

    #是否为新设备
    def is_newdev(self):
        deviceid = self.get_deviceid()
        if deviceid:
            is_new = self.data.get_newdev(deviceid)                     # 对比数据库mac和添加
            print(is_new)

    #设备：新设备状态
    def set_newdev(self,st='1'):
        st = {'key':'new_dev','value':st,'nona':'是否为新设备'}         # st等于字典
        self.data.up_config(st);                                        # 在数据库更新写入st字典

    # 本地设置的城市数据
    def city_data(self):
        conf = self.data.getconfig()

        if 'city' in conf:  #if 后，在不在conf,字典内
            re_json = {'city':conf['city'],'city_cnid':conf['city_cnid']}
            return json.dumps(re_json)
        else:
            url = self.config['httpapi'] + '/raspberry/get_city.html'            #从远程获取城市数据
            res = self.mylib.http_post( url )
            if (res['code']=='0000'):
                tab = json.loads( res['data'] )

                add_data = [{'key':'city','value':tab['location'],'nona':'当前城市'},{'key':'city_cnid','value':tab['cid'],'nona':'当前城市天气ID'}]
                self.data.setconfig(add_data)                                #写入数据库

                re_json = {'city':tab['location'],'city_cnid':tab['cid']}
                return json.dumps(re_json)


    #用户绑定操作
    def user_bind(self, postjson):
        re_json = {"code":'9999',"msg":"绑定操作失败，请重新操作"}
        if not type(postjson) is dict:
            self.Mqtt.send_admin('xiaocx', 'USER_REG', re_json )
            return

        info = self.data.user_reg( postjson )
        if info['state'] < 0:           #用户信息格式错误
            re_json = {"code":'1001',"msg":info['msg']}
        elif info['state'] == 0:        #绑定新用户信息失败
            re_json = {"code":'2001',"msg":info['msg']}
        elif info['state'] == 1:        #已经绑到此设备
            re_json = {"code":'0001',"data": info['data'], "msg":info['msg']}
        elif info['state'] == 2:        #绑定新用户信息成功
            re_json = {"code":'0000',"data": info['data'], "msg":info['msg']}

        self.Mqtt.send_admin('xiaocx', 'USER_REG', re_json )

        if int(info['state']) >= 1:
            uid = info['data']['uid']
            self.user_face_bind(uid)

    #用户人脸绑定
    def user_face_bind(self, uid ):
        import os,time
        from package.include.eyes.opencv import Opencv        #人脸离线识别

        #保存用户图像成功
        temp_photo = os.path.join(self.config['root_path'], "data/shijue/photos_"+ str(uid) +".jpg")
        ding_wav = os.path.join(self.config['root_path'], "data/snowboy/ding.wav")

        def success( is_succ, cap, cv2 ):
            if is_succ:
                postup = {'facepath':temp_photo}
                res = self.data.user_up( uid, postup )
                os.popen("sudo aplay "+ ding_wav )
                time.sleep(1)
                cap.release()
                cv2.destroyAllWindows()
                #取消显示二维码导航消息
                self.Mqtt.send_nav(  {"event" : "close"} )
                re_json = {"code":'0003', "msg":'人脸图像已经保存成功'}
                self.Mqtt.send_admin('xiaocx', 'USER_REG', re_json )



            else:
                start_video()

        opencv = Opencv()
        opencv.success = success

        fier_file  = os.path.join(self.config['root_path'], "data/shijue/haarcascade_frontalface_default.xml")
        fier_file2 = os.path.join(self.config['root_path'], "data/shijue/haarcascade_righteye_2splits.xml")

        param = {
            'temp_file': temp_photo,
            'fier_file':{
                'file': fier_file,
                'scaleFactor': 1.2,     #多少倍
                'minNeighbors': 6,      #对比多少次
                'minSize': (40, 40)
            },
            'fier_file2':{
                'file': fier_file2,
                'scaleFactor': 1.2,
                'minNeighbors': 6,
                'minSize': (40, 40)
            },
            'show_win':True
        }
        def start_video():
            opencv.main_video( param )

        start_video()



     #用户修改
    def user_edit(self,name):
        '''
        * 更新用户表数据
        * uid       --  用户uid
        * updata    --  更新数据(字典)
        '''
        have = self.data.user_up(name["uid"],name["switch"])
        if have:
            self.Mqtt.send_admin('xiaocx', 'USER_EDIT',{"code":'0000',"msg":"用户信息修改成功"})
        else:
            self.Mqtt.send_admin('xiaocx', 'USER_EDIT',{"code":'2001',"msg":"用户修改信息失败"})

    #用户删除
    def user_dels(self,name):

        have = self.data.user_del(name["uid"])
        if have:
            self.Mqtt.send_admin('xiaocx', 'USER_REMOVE',{"code":'0000',"msg":"删除用户信息成功"})
        else:
            self.Mqtt.send_admin('xiaocx', 'USER_REMOVE',{"code":'2001',"msg":"删除用户信息失败"})

    #打开和关闭屏幕
    def device_screen(self,name):
        try:
            import package.include.skills.action.screens as screens
            have = name["value"]
            if have == "0" or have == 0:
                if  screens.Screen().main("off") :
                    self.Mqtt.send_admin('xiaocx', 'DEVICE_SCREEN',{"code":"0000","msg":"屏幕关闭"})
                else:
                    self.Mqtt.send_admin('xiaocx', 'DEVICE_SCREEN',{"code":"9999","msg":"操作屏幕失败"})

            elif have == "1" or have == 1:
                if have == screens.Screen().main("on"):
                    self.Mqtt.send_admin('xiaocx', 'DEVICE_SCREEN',{"code":"0000","msg":"屏幕打开"})
                else:
                    self.Mqtt.send_admin('xiaocx', 'DEVICE_SCREEN',{"code":"9999","msg":"操作屏幕失败"})

            else:
                self.Mqtt.send_admin('xiaocx', 'DEVICE_SCREEN',{"code":"9999","msg":"操作屏幕失败"})
        except:
            self.Mqtt.send_admin('xiaocx', 'DEVICE_SCREEN',{"code":"9999","msg":"操作屏幕失败"})
    #设置音量
    def device_volume(self,name):
        try:
            import package.include.skills.action.voices as voices

            have = voices.Voices().main(str(name["value"]))
            if have:
                self.Mqtt.send_admin('xiaocx', 'DEVICE_VOLUME',{"code":"0000","msg":str(name["value"]) })
            else:
                self.Mqtt.send_admin('xiaocx', 'DEVICE_VOLUME',{"code":"9999","msg":"设置声音失败"})

            os.system("sudo aplay {0}".format(os.path.join(self.config['root_path'],"data/yuyin/ding.wav")))
        except:
            self.Mqtt.send_admin('xiaocx', 'DEVICE_VOLUME',{"code":"9999","msg":"设置声音失败"})
    #获取初始音量
    def device_init_volume(self):
        try:
            import package.include.skills.action.voices as voices
            have = voices.Voices().chushizhi()
            if have:
                self.Mqtt.send_admin('xiaocx', 'DEVICE_STATE', { "code":"0000","info":{"sound": str(int(have))   }})
            else:
                self.Mqtt.send_admin('xiaocx', 'DEVICE_STATE',{ "code":"9999","info":{"sound":"获取当前设备音量失败"}})
        except:
            self.Mqtt.send_admin('xiaocx', 'DEVICE_STATE',{ "code":"9999","info":{"sound":"获取当前设备音量失败"}})


    #屏幕初始化状态
    def device_init_screen(self):
        try:
            import package.include.skills.action.screens as screens
            have = screens.Screen().init_screen()
            if have =="1" or have =="0":
                self.Mqtt.send_admin('xiaocx', 'DEVICE_STATE',{ "code":"0000","info":{"screen":have}})
            else:
                self.Mqtt.send_admin('xiaocx', 'DEVICE_STATE',{ "code":"9999","info":{"screen":"屏幕初始化状态失败"}})
        except:
            #self.Mqtt.send_admin('xiaocx', 'DEVICE_STATE',{ "code":"9999","info":{"screen":"屏幕初始化状态失败"}})
            self.Mqtt.send_admin('xiaocx', 'DEVICE_STATE',{ "code":"0000","info":{"screen":"1"}})

    # 获取设备全部状态
    def device_s(self):
        try:
            have_volume = voices.Voices().chushizhi()
            have_screen = screens.Screen().init_screen()
            print(have_volume,have_screen)
            if have_volume and have_screen:
                self.Mqtt.send_admin('xiaocx', 'DEVICE_STATE', { "code":"0000","info":{"screen":have_screen ,"sound":    str(int(have_volume))   }})
            else:
                self.Mqtt.send_admin('xiaocx', 'DEVICE_STATE', { "code":"9999","info":{"screen":"屏幕初始化状态失败","sound":"获取当前设备音量失败"}})
        except:
            #self.Mqtt.send_admin('xiaocx', 'DEVICE_STATE', { "code":"9999","info":{"screen":"屏幕初始化状态失败","sound":"获取当前设备音量失败"}})
            self.Mqtt.send_admin('xiaocx', 'DEVICE_STATE', { "code":"0000","info":{"screen":'1' ,"sound": "60"  }})

    # 旋转屏幕
    def device_rturn(self,name):
        self.Mqtt.send_admin('xiaocx', 'DEVICE_RTURN', { "code":"0000"})
        os.system("sudo python3 {0}".format(os.path.join(self.config['root_path'],"package/include/rotatingscreen.py")))

    # 获取硬件状态
    def u_device(self,name):
        import package.include.skills.action.screens as screens
        import package.include.skills.action.voices as voices
        # 获取全部当前状态
        if name["state"] == "all":
            self.device_s()

        # 获取音量当前状态
        elif name["state"] == "volume":
            self.device_init_volume()

        # 获取屏幕当前状态
        elif name["state"] == "screen":
            self.device_init_screen()



def main():
    pass


if __name__ == '__main__':
    pass
    '''
    print(device().device_screen({"switch":"off"}))
    print(device().device_screen({"switch":"on"}))
    print(device().device_volume({"switch":"60"}))
    print(device().user_dels({"uid":"2"}))
    print(device().user_edit({"uid":"1","switch":{"realname":"徐大大","nickname":"小黑"}}))
    '''
   # device().Mqtt.send_nav(  {"event" : "close",} )

