from MsgProcess import MsgProcess, MsgType
import time,os,re
import RPi.GPIO as GPIO


class Plug_in_Library(MsgProcess):

    def Start(self,x):
        os.system("sudo chmod 777 plugin/Plug_in_Library")
        os.system("sudo pip3 install qrcode")
        

    def Text(self, message):
        
        try:
            try:
                import qrcode#二维码模块
            except:
                self.say("插件库启动失败，确保网络正常并且重新开机！")   
                return 0

            if not "关闭" in message["Data"]:
                ipAddrs = os.popen("hostname -I").read()   # 取IP地址
                if ipAddrs:  # 如果有IP
                    ipAddrs=re.split(r'\s',ipAddrs)[0]
                    img=qrcode.make("http://"+ipAddrs+":8088")#二维码生成函数
                    img.save("plugin/Plug_in_Library/data.png")#生成后的位子
                    datas = {  "type":"exejs","data":"set_Plug_in_Library_play({0})".format( {"data":"/plugin/Plug_in_Library/data.png"})   }
                    self.send( MsgType=MsgType.Text, Receiver="Screen", Data= datas )
                    self.say("正在打开插件库,请使用微信扫一扫。")                                                      
            else:
                datas = {  "type":"exejs","data":"set_Plug_in_Library_exit()" }
                self.send( MsgType=MsgType.Text, Receiver="Screen", Data= datas )
                self.say("已关闭插件库")     
        except:
            self.say("插件库启动失败，请重试！")     
