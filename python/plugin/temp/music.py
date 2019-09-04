import os,re,random,time
import threading as td
import multiprocessing as mp#创建进程
#播放歌曲主类
class Music():
    this_path = os.path.dirname(os.path.dirname(__file__))
    def __init__(self,ojt):
        self.is_snowboy = ojt.is_snowboy
        data = "./ga.py"
        out = os.popen("ps ax | grep "+data).read()
        pat = re.compile(r'(\d+).+('+data+')')
        res = pat.findall(out)

        if len(res) <=2:
            #print("音乐不存在")
            os.popen("sudo python3 {0}".format(os.path.join(self.this_path,"action/ga.py")))

            #唤醒后暂停音乐进程
            pl = mp.Process(target = self.snowboy_stop_music )#创建进程1
            #pl.daemon = True #定义守护进程
            pl.start()#启动进程1
        else:
            print("音乐存在")
            #for x in res:
            #    pid = x[0]
            #    cmd = 'sudo kill -9 '+ pid
            #    out = os.popen(cmd).read()
            #exit()

    #唤醒后暂停音乐
    def snowboy_stop_music(self):
        while 1:
            if self.is_snowboy.value !=0:
                self.postmusic("暂停")
            #时间太大会捕获错过 不可以超过0.3
            time.sleep(0.2)

    def postmusic(self,name):
        wfPath = "/p2"
        try:os.mkfifo(wfPath)
        except OSError: pass
        wp = open(wfPath, 'w')
        wp.write(name)
        wp.close()

    def main(self,name):
        self.postmusic(name["txt"])
        if name["txt"][2:]=="。":
            return {'state':True,'data':"我猜你是要听歌曲吧，一起来听",'msg':'','stop':True}
        else:
            return {'state':True,'data':"一起来听",'msg':'','stop':True}

    def musicxiayiqumain(self,name):
        self.postmusic("下一曲")
        return {'state':True,'data':"",'msg':'','stop':True}

    def musicshangyiqumain(self,name):
        self.postmusic("上一曲")
        return {'state':True,'data':"",'msg':'','stop':True}

    def musicpause(self,name):
        self.postmusic("暂停")
        return {'state':True,'data':"",'msg':'','stop':True}

    def musicnext(self,name):
        self.postmusic("继续")
        return {'state':True,'data':"",'msg':'','stop':True}

    def musicstop(self,name):
        self.postmusic("停止")
        return {'state':True,'data':"",'msg':'','stop':True}
    #笑话
    def joke(self,name):
        str_ = ["播放爆笑","播放搞笑","播放爆笑办公室","播放喜剧听我的"]
        str_ = str_[ random.randint(0,len(str_)-1) ]
        self.postmusic(str_)
        return {'state':True,'data':"一起来听",'msg':'','stop':True}
    #故事
    def story(self,name):
        str_ = ["播放一米阳光音乐台",]
        str_ = str_[ random.randint(0,len(str_)-1) ]
        self.postmusic(str_)
        return {'state':True,'data':"一起来听",'msg':'','stop':True}


if __name__ == '__main__':
    m = Music("ojt")
    music = {"txt":"播放不哭了by2"}
    m.musicshangyiqumain(1)



