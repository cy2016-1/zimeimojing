import requests,os,time,re,string,math,random,pygame,threading,setproctitle #自定义进程名称模块
import multiprocessing as mp    #多进程
from package.include.skills.plugin_object import Plugin_object

class Music( Plugin_object ):
    name = 'music'
    def __init__(self,public_obj):

        self.public_obj = public_obj
        #停止歌曲变量
        self.musicstopstop = 0
        #下一曲变量
        self.musicst_lower = 0
        #上一曲变量
        self.last_song     = 0

        if self.voices() > 80:
            os.system("sudo amixer set Speaker 80%")

        #检查根目录下有没有音乐文件夹
        if os.path.exists('/musics') ==False:
            os.mkdir('/musics')#创建

        #自定义停止线程名称
        #data = self.name
        #out = os.popen("ps ax | grep "+data).read()
        #pat = re.compile(r'(\d+).+('+data+')')
        #res = pat.findall(out)
        #print(res)
        #if len(res) <=2:
        #    print("音乐不存在")
        #    ##创建start_music进程
        #    start_music_process = mp.Process(target = self.start_music)
        #    start_music_process.start()

        #else:
        #    print("音乐存在")
            #for x in res:
            #    pid = x[0]
            #    cmd = 'sudo kill -9 '+ pid
            #    os.system(cmd)


    #发送文字到屏幕
    def postmojing(self,txt):

        try:
            self.public_obj.sw.send_info( {'obj':'mojing','msg': txt} )
        except:
            pass
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
    def musicdel(self,path='/musics/'):
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
    def playmusic(self,ID):
        print("进入了playmusic",self.musicid,ID)
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

        #进程的不同所有操作上下歌曲时依次在内部停止歌曲
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.stop()
        #发送到前面屏幕

        self.postmojing("歌曲音量太大导致语音唤醒困难，使用微信小程序控制音量")
        if os.path.exists("/musics/"+play+".mp3") ==False:
            self.postmojing("正在缓冲："+play)
            r = requests.get(data, stream=True, timeout = 30)
            f = open("/musics/{0}.mp3".format(play), "wb")
            for chunk in r.iter_content(chunk_size=512):

                if chunk:
                    f.write(chunk)

                #停止循环  停止音乐  停止线程  主进程存在
                if self.musicstopstop == 1:
                    self.musicstopstop = 0
                    return "stop"
                #下个曲
                if self.musicst_lower == 1:
                    self.musicst_lower = 0
                    return "lower"
                #上一曲
                if self.last_song == 1:
                    self.last_song = 0
                    return  "song"

                #唤醒后暂停
                if self.pause() != 0:
                    return "stop"



        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.set_volume(1)#调整音量最多1
        self.postmojing("正在播放："+play)
        file = "/musics/{0}.mp3".format(play)
        file = file.encode('utf-8')
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():

            #停止循环  停止音乐  停止线程  主进程存在
            if self.musicstopstop == 1:
                self.musicstopstop = 0
                return "stop"
            #下个曲
            if self.musicst_lower == 1:
                self.musicst_lower = 0
                return "lower"
            #上一曲
            if self.last_song == 1:
                self.last_song = 0
                return  "song"
            #设置声音继续播放
            elif self.keepon() != 0:
                pygame.mixer.music.unpause()
               # self.postmusic("继续")
            #唤醒后暂停
            elif self.pause() != 0:
                pygame.mixer.music.pause()
                #self.postmusic("暂停")
            time.sleep(0.8)

        return "lower"


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
    def for_paly(self,name):
        #删除音乐缓存
        self.musicdel()
        print("进入了while_paly")
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
        #self.ID_ints变量必须使用self传递，不然在多次线程里不稳定，会被重置
        self.ID_ints = 0
        while 1:
            try:
                ID = self.musicid[self.ID_ints]
                print(ID,self.ID_ints,"播放id"*10)
                have = self.playmusic(ID)

                if have == "stop" :
                    print("线程彻底结束")
                    pygame.mixer.music.stop()
                    break

                elif have == "song":
                    self.ID_ints -=1
                    if self.ID_ints < 0 :self.ID_ints=0

                elif have == "lower":
                    self.ID_ints +=1

            #列表播放完成 最后会超出索引停止循环播放
            except:
                break
        print("线程彻底结束2")



    #start_music初始化被进程启动了，通过歌曲指令调用了start_play线程播放歌曲
    def start_play(self,name):
        print("进入start_play")
        start_music_process = mp.Process(target = self.start_music)
        start_music_process.start()
        #开始新的歌曲停止前面的歌曲线程
        self.musicstopstop = 1
        time.sleep(1)
        t = threading.Thread(target = lambda : self.for_paly(name) )
        self.musicstopstop = 0
        t.start()


    #start_music初始化被进程启动了
    def start_music(self):
        print("进入start_music")
        #修改进程名称
        setproctitle.setproctitle(self.name)
        while 1:
            try:
                name = self.get(self.name)
                #找到触发词后面词文字开始的位置
                path = re.search(name["trigger"], name["txt"]).span()[-1]
                #所有播放意图的触发指令后面没有歌曲名就我们自定义推荐
                if name["txt"][path:]=="。" :
                    self.post(self.name,{'state':True,'data':"我猜你是要听歌曲吧，一起来听",'msg':'','stop':True})
                    self.start_play("90后歌曲")

                else:
                    #播放意图的触发指令后面歌曲名
                    print("执行了"*100)
                    self.post(self.name,{'state':True,'data':"一起来听"+name["txt"][path:],'msg':'','stop':True})
                    self.start_play(name["txt"][path:])






                #if response =="暂停":
                #    pygame.mixer.music.pause()
                #elif response =="继续":
                #    pygame.mixer.music.unpause()
                #elif response =="停止":
                #    self.musicstopstop = 1
                #elif response =="下一曲":
                #    self.musicst_lower = 1
                #elif response =="上一曲":
                #    self.last_song     = 1
                ##播放
                #else:

               # os.system("sudo aplay /var/www/server/python/data/snowboy/ding.wav")
            except:
                time.sleep(0.3)

    #写入内存变量
    #def postmusic(self,name):
    #    wfPath = "/mojingmusic"
    #    try:os.mkfifo(wfPath)
    #    except OSError: pass
    #    wp = open(wfPath, 'w')
    #    wp.write(name)
    #    wp.close()

    def main(self,name):
        print("进入了main")
        #找到触发词后面词文字开始的位置
        path = re.search(name["trigger"], name["txt"]).span()[-1]
        #所有播放意图的触发指令后面没有歌曲名就我们自定义推荐
        if name["txt"][path:]=="。" :
            self.post(self.name,{'state':True,'data':"我猜你是要听歌曲吧，一起来听",'msg':'','stop':True})
            self.start_play("90后歌曲")

        else:
            #播放意图的触发指令后面歌曲名
            self.post(self.name,{'state':True,'data':"一起来听"+name["txt"][path:],'msg':'','stop':True})
            self.start_play(name["txt"][path:])






    #def musicxiayiqumain(self,name):
    #    self.postmusic("下一曲")
    #    return {'state':True,'data':"",'msg':'','stop':True}

    #def musicshangyiqumain(self,name):
    #    self.postmusic("上一曲")
    #    return {'state':True,'data':"",'msg':'','stop':True}

    #def musicpause(self,name):
    #    self.postmusic("暂停")
    #    return {'state':True,'data':"",'msg':'','stop':True}

    #def musicnext(self,name):
    #    self.postmusic("继续")
    #    return {'state':True,'data':"",'msg':'','stop':True}

    #def musicstop(self,name):
    #    self.postmusic("停止")
    #    return {'state':True,'data':"",'msg':'','stop':True}
    ##笑话
    #def joke(self,name):
    #    str_ = ["播放爆笑","播放搞笑","播放爆笑办公室","播放喜剧听我的"]
    #    str_ = str_[ random.randint(0,len(str_)-1) ]
    #    self.postmusic(str_)
    #    return {'state':True,'data':"一起来听",'msg':'','stop':True}
    ##故事
    #def story(self,name):
    #    str_ = ["播放一米阳光音乐台",]
    #    str_ = str_[ random.randint(0,len(str_)-1) ]
    #    self.postmusic(str_)
    #    return {'state':True,'data':"一起来听",'msg':'','stop':True}

if __name__ == '__main__':
    c =Music(1)
    #music = {"txt":"播放by2"}
  #  c.main(music)
    c.postmusic("暂停")