import requests,os,time,re,string,math
import multiprocessing as mp#创建进程
import pygame
import threading


def import_path(return_path = -3):
    #在脚本导入环境内添加索引位置
    #当前脚本位置上去几层就写负几层
    #下面所有导入全部都支持在该目录目录
    #脚本环境位置不发生改变，只是import多了一个查找位置
    import sys,os
    biao = []
    ints_= 0
    this_path = os.path.dirname(os.path.dirname(__file__))

    for x in this_path:
        if x=="/":biao.append(ints_)
        ints_+=1

    sys.path.append(    this_path[:biao[return_path]]   )

import_path()

import package.mysocket as mysocket                     #发送websocket
#==================================================
#播放歌曲类
#==================================================
class Music2():
    def __init__(self):
        if self.voices() > 80:
            os.system("sudo amixer set Speaker 80%")

        #检查根目录下有没有音乐文件夹
        if os.path.exists('/music') ==False:
            os.mkdir('/music')#创建
        self.musicdil()
        pygame.mixer.init()
        #保证只要一个音乐线程
        self.kill = 0
        #停止歌曲
        self.musicstopstop = 0
    #当前音量
    def voices(self):
        jieguo,jiance=str(),'['
        huoqu_os=os.popen("sudo amixer scontents | grep 'Front Left: Playback'|grep 'dB'").read()
        for x in re.sub(r'^.*k','',re.sub(r'].*$','',huoqu_os[len(re.sub(r'F.*$','',huoqu_os)):])):
            if x==jiance:
                jiance="kaishi"
            elif jiance=="kaishi":
                jieguo+=x
        #通过y = 1.7972e^(0.04x) x为填入的音量，y为实际音量 这个公式计算出实际音量。
        return 1.7972 * math.pow(2.718,0.04 * int(jieguo[:-2]))

    #音乐删除
    def musicdil(self,path='/music/'):
        try:
            if len(os.listdir(path)) <100:
                print("不需要清理")
                return
            datatime=[]
            for x in os.listdir(path):
                #记录所有歌曲的最后访问时间
                datatime.append(os.stat(path+x)[-3])
            #列表有小到大排列,和去重
            datatime.sort()
            deldata = list(set(datatime[:10]))
            '''
            for x in deldata:
                print("时间为：",time.strftime("%Y--%m--%d %H:%M:%S", time.localtime(x)))

            print("符合删除",deldata)
            '''
            ints = 0
            #循环所有歌曲
            for x in os.listdir(path):
               # print(x)
                #循环删除符合要求的
                for y in deldata:
                    #在所有歌曲中寻找=符合删除要求的歌曲
                    try:
                        if y == os.stat(path+x)[-3]:
                            ints +=1
                            #删除10首结束
                            if ints > 10:
                                break
                            os.system("sudo rm -r {0}{1}".format(path,x))
                            print(" 正在删除：{0}{1}".format(path,x))
                    #这个是为了防止已经删除的文件，还在内存列表里还是循环继续删除，导致错误
                    except:pass

        except Exception as bug :print("音乐删除错误"*100,bug)

    #发送文字到屏幕
    def postmojing(self,txt):
        try:
            mysocket.Mysocket().send_info( {'obj':'mojing','msg': txt} )
        except:
            pass

    #播放歌曲方法
    def playmusic(self,ID):

        ints = self.musicid.index(ID)
        #去符号方法
        play = re.sub( '[%s]' % re.escape( string.punctuation ), '-',self.musicname[ints] )


        data = self.http_post(url ="http://antiserver.kuwo.cn/anti.s?type=convert_url&rid="+ID+"&format=mp3&response=url")
        #歌曲链接
        if data["code"] =="404":
            self.postmojing("没有找到该歌曲,你可以这样搜索,流行歌曲,90后歌曲,纯音乐等等")
            return

        if data["code"] =="9999":
            self.postmojing("网络可能有点问题")
            return

        data= data["data"]

        a68 = os.path.exists("/music/"+play+".mp3")#检查
        #进程的不同所有操作上下歌曲时依次在内部停止歌曲
        pygame.mixer.music.stop()
        #发送到前面屏幕
        self.postmojing("正在播放："+play)
        self.postmojing("歌曲音量太大导致语音唤醒困难，使用微信小程序控制音量")
        if a68 ==False:
            print("正在缓冲")
            r = requests.get(data, stream=True, timeout = 30)
            f = open("/music/{0}.mp3".format(play), "wb")
            for chunk in r.iter_content(chunk_size=512):
                if chunk:
                    f.write(chunk)


        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.set_volume(1)#调整音量最多1
        print("正在播放：",play,ID)
        self.off  =0
        while 1:

            if not pygame.mixer.music.get_busy():

                print(play,"----->",ID)
                file = "/music/{0}.mp3".format(play)
                file = file.encode('utf-8')
                pygame.mixer.music.load(file)
                pygame.mixer.music.play()
                self.off+=1
                print(self.off)
                #停止循环  停止音乐  停止线程  主进程存在
                if self.musicstopstop == 1:
                    self.musicstopstop = 0
                    pygame.mixer.music.stop()
                    return False
               # time.sleep
                if self.off == 2:
                    print("播放完成，即将下一曲")
                    return


            else:
                #停止循环  停止音乐  停止线程  主进程存在
                if self.musicstopstop == 1:
                    self.musicstopstop = 0
                    pygame.mixer.music.stop()
                    return False
                #保证只要一个音乐线程
                if self.kill == 1:
                    print("线程被杀")
                    self.kill = 0
                    break
        return False




    def http_post(self,url):

        try:
            response  = requests.get(url, timeout = 5)
            res = {'code':'404','msg':'网络请求失败！','data':''}
            if response.status_code==200:
                res['code'] = '0000'
                res['msg']  = '请求成功！'
                res['data'] = response.text
                return res
            else:
                return res
        #没有网络或者请求超时依然返回,正常情况下也返回
        except:
            return {'code':'9999','msg':'网络错误！','data':''}

#==================================================
#播放歌曲方法
#==================================================
    def __main(self,name):
        try:
            #重复点歌时关闭前面歌曲循环
            if self.off == 1:
                self.kill = 1
        except:pass

        url="http://search.kuwo.cn/r.s?all="+ name +"&ft=music&itemset=web_2013&client=kt&pn=0&rn=10&rformat=json&encoding=utf8&rn=1&rformat=json&encoding=utf8"
        data = self.http_post(url =url)

        #print(type(data["data"]))
        #得到数据
        if data["code"] =="404":
            self.postmojing("没有找到该歌曲,你可以这样搜索,流行歌曲,90后歌曲,纯音乐等等")
            return
        if data["code"] =="9999":
            self.postmojing("网络可能有点问题")
            return

        have = data["data"]
        #解析数据
        text = eval(have)["abslist"]
        #锁定数据
        self.musicname = []
        self.musicid   = []
        for x in text:
            self.musicid.append(x['MUSICRID'])
            self.musicname.append(x['NAME']+"-"+x['ARTIST'])
        postdata='<br>'.join(self.musicname)
        self.postmojing("歌曲列表："+postdata)
        print( self.musicid)
        print(self.musicname)

        for ID in self.musicid:
            self.globalID = ID
            print("播放1"*100)
            have = self.playmusic(ID)
            print("线程彻底结束")
            if have ==False:return



    def main(self,name):
        self.musicdil()

        t = threading.Thread(target = lambda x = name : self.__main(x) )
        t.start()


#================================================================================
#歌曲上一首方法
#=================================================================================

    def musicshangyiqu(self):
        self.kill = 1
        ints = self.musicid.index(self.globalID)
        #===========================================
        #如果连续上一曲 就会导致列表里的超出索引
        #如果歌曲已经是在列表0那么再次上一曲就还在0
        #ID = 歌曲在服务器上的位置
        #play = 对应ID的歌曲名
        #===========================================
        if  ints == 0:
            self.globalID = self.musicid[ints]

        else:
            self.globalID = self.musicid[ints-1]

        have = self.playmusic(self.globalID)
        print("线程彻底结束")
        if have ==False:return
        #===========================================
        #上一曲播放完毕后开始恢复正常循环播放顺序
        #不过需要跳过已经播放的歌曲
        #ints2= 历史歌曲计数器
        #ints = 上一曲之前的歌曲计数器
        #===========================================
        ints2=0
        for ID in self.musicid:
            if ints2 >= ints:
                self.globalID = ID
                have = self.playmusic(ID)
                print("线程彻底结束")
                if have ==False:return

            else:
                print("tiaoguo"*100)
                ints2+=1

    def musicshangyiqumain(self,name):
        if not pygame.mixer.music.get_busy():
            self.postmojing("请先播放")
        else:
            t = threading.Thread(target = self.musicshangyiqu)
            t.start()


#==============================================================
#歌曲下一首方法
#===============================================================

    def musicxiayiqu(self):
        self.kill = 1
        ints = self.musicid.index(self.globalID)
        #===========================================
        #如果连续下一曲 就会导致列表里的超出索引
        #如果歌曲已经是在列表0那么再次上一曲就还在0
        #ID = 歌曲在服务器上的位置
        #===========================================
        if  ints == len(self.musicid)-1:
            self.globalID = self.musicid[ints]
        else:
            self.globalID = self.musicid[ints+1]

        have  = self.playmusic(self.globalID)
        print("线程彻底结束")
        if have ==False:return
        #===========================================
        #上一曲播放完毕后开始恢复正常循环播放顺序
        #不过需要跳过已经播放的歌曲
        #ints2= 历史歌曲计数器
        #ints = 上一曲之前的歌曲计数器
        #===========================================

        ints2=0
        for ID in self.musicid:
            if ints2 >= ints:
                self.globalID = ID
                have = self.playmusic(ID)
                print("线程彻底结束")
                if have ==False:return
            else:
                ints2+=1

    def musicxiayiqumain(self,name):
        if not pygame.mixer.music.get_busy():
            self.postmojing("请先播放")
        else:
            t = threading.Thread(target = self.musicxiayiqu )
            t.start()


    #暂停播放
    def musicpause(self,x):
        pygame.mixer.music.pause()

    #继续播放
    def musicnext(self,x):
        if not pygame.mixer.music.get_busy():
            self.postmojing("请先播放")
        else:
            pygame.mixer.music.unpause()

    #停止播放
    def musicstop(self,x):
        self.musicstopstop = 1


if __name__ == '__main__':
    a = Music2()
    rfPath = "/p2"
    while 1:
        try:
            rp = open(rfPath, 'r')
            response = rp.read()
            rp.close()



            if response[:4] =="播放一首" or response[:4] =="播放一个" or \
            response[:4] =="播放歌曲" or response[:4] =="播放音乐" or response[:2] =="。":

                if response[2:] == "。" or  response[4:] == "。" :
                    a.main("90后歌曲")
                else:
                    a.main(response[4:] )

                os.system("sudo aplay /var/www/server/python/data/snowboy/ding.wav")
            elif response[:2] =="播放":
                a.main(response[2:])
            elif response =="下一曲":
                a.musicxiayiqumain(1)
            elif response =="上一曲":
                a.musicshangyiqumain(1)
            elif response =="暂停":
                a.musicpause(1)
            elif response =="继续":
                a.musicnext(1)
            elif response =="停止":
                a.musicstop(1)
            #os.system("sudo aplay /var/www/server/python/data/snowboy/ding.wav")

        except:
            time.sleep(0.3)



