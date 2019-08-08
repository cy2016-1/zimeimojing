import urllib,os
from package.base import Base       #基本类
import package.mymqtt as mymqtt

class User(Base):
    def __init__(self, public_obj):
        self.public_obj = public_obj
        self.Mqtt = mymqtt.Mymqtt(self.config)

    #用户绑定操作
    def user_bind(self, postjson):

        postjson = postjson['data']
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
            return {'state':False,'data': "注册完成",'msg':'','type':'system'}


    #用户人脸绑定
    def user_face_bind(self, uid ):

        if self.config['CAMERA']['enable']==False:
            '''系统配置为不启用摄像头'''
            self.public_obj.sw.send_nav({"event" : "close"})                 #取消显示二维码导航消息
            re_json = {"code":'0003', "msg":'系统配置为不启用摄像头'}
            self.Mqtt.send_admin('xiaocx', 'USER_REG', re_json )
            return

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
                self.public_obj.sw.send_nav({"event" : "close"})
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


    #用户注销
    def user_dels(self,name):

        have = self.data.user_del(name["data"]["uid"])

        if have["state"]:
            self.Mqtt.send_admin('xiaocx', 'USER_REMOVE',{"code":'0000',"msg":"注销用户信息成功"})
            return {'state':False,'data': "注销完成",'msg':'','type':'system'}
        else:
            self.Mqtt.send_admin('xiaocx', 'USER_REMOVE',{"code":'2001',"msg":"注销用户信息失败"})
            return {'state':False,'data': "注销失败",'msg':'','type':'system'}
     #用户修改
    def user_edit(self,name):
        '''
        * 更新用户表数据
        * uid       --  用户uid
        * updata    --  更新数据(字典)
        '''
        have = self.data.user_up(name["data"]["uid"],name["data"]["updata"])
        if have:
            self.Mqtt.send_admin('xiaocx', 'USER_EDIT',{"code":'0000',"msg":"用户信息修改成功"})
        else:
            self.Mqtt.send_admin('xiaocx', 'USER_EDIT',{"code":'2001',"msg":"用户修改信息失败"})

if __name__ == '__main__':
    pass
    #User().user_bind()