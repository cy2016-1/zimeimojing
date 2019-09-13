import os,time
from package.base import Base,log

from package.include.eyes.opencv import Opencv        #人脸离线识别
import package.include.baiduapi.contrast as contrast    #人脸在线对比

class Visual(Base):
    """视觉类"""

    def __init__(self):
        log.info("初始化人脸对比")

        self.temp_photo = os.path.join(self.config['root_path'], "runtime/photos.jpg")

        self.is_video = False           # 是否启动人脸识别
        self.video_i = 0
        self.video_max = 10

        self.opencv = Opencv()          #人脸识别类
        self.opencv.success = self.success

        self.contrast = contrast.Contrast_face()        #人脸在线对比


        #人脸识别应用().注册()
        #人脸识别应用().扫描()
        #人脸识别应用().修改资料()

    #开始使用百度在线人脸对比
    def start_contrast_face(self, user_info, i = 0 ):
        if i >= len(user_info) : return 0
        this_info = user_info[i]
        facepath = this_info['facepath']
        log.info('facepath',facepath)
        if facepath != None:
            if os.path.isfile(facepath):
                bjz = self.contrast.main( facepath, self.temp_photo )
                log.info('对比值:',this_info['uid'], bjz )
                if bjz >= 80:
                    return this_info['uid']
        i += 1
        time.sleep(0.2)
        return self.start_contrast_face(user_info, i )

    #抓拍人脸成功
    def success(self, is_succ, cap, cv2):
        cap.release()
        cv2.destroyAllWindows()
        if self.video_i >= self.video_max:
            return
        if is_succ:
            uid = self.start_contrast_face( self.user_info, 0 )
            if uid <= 0:
                self.start_video()
            else:
                data= {
                'enter': 'camera',
                'type': 'system',
                'state': True,
                'msg': '识别成功',
                'data': '',
                'body': uid
                }
                self.command_execution(data)

        else:
            self.start_video()

    #开始抓拍人脸
    def start_video(self):
        self.video_i += 1
        fier_file  = os.path.join(self.config['root_path'], "data/shijue/haarcascade_frontalface_default.xml")
        #fier_file2 = os.path.join(self.config['root_path'], "data/shijue/haarcascade_righteye_2splits.xml")
        param = {
            'temp_file': self.temp_photo,
            'fier_file':{
                'file': fier_file,
                'scaleFactor': 1.8,     #多少倍
                'minNeighbors': 4,      #对比多少次
                'minSize': (64, 64)
            },
            'show_win':True
        }

        self.opencv.main_video( param )

    def main(self, command_execution ):
        self.command_execution = command_execution
        self.user_info = self.data.user_list_get('uid,facepath')
        if self.user_info == False:
            log.info('暂无用户数据，人脸对比停止！')
            return
        if len(self.user_info) > 0:
            for x in self.user_info:
                if x['facepath'] == None:continue
                if len(x['facepath'])>0:
                    if os.path.isfile(x['facepath']):
                        self.is_video = True
            if self.is_video:self.start_video()

