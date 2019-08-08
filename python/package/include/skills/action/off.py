import re,os
class Off():
    def __init__(self, public_obj):
        pass
    def stop( self ):
        data = "./ga.py"
        out = os.popen("ps ax | grep "+data).read()
        pat = re.compile(r'(\d+).+('+data+')')
        res = pat.findall(out)
        if len(res) <=2:
            pass
           # print("音乐不存在")
        else:
            wfPath = "/p2"
            try:
                os.mkfifo(wfPath)
            except OSError:
                pass

            wp = open(wfPath, 'w')
            wp.write("停止")
            wp.close()

    def main(self,name):

       # if re.search(name["cmd"],name["txt"]).span()[0] == 0:
        try:
            self.stop()
        except:pass
        return {'state':True,'data': "",'msg':'参数1，需要输入字典类型！','stop':True}
