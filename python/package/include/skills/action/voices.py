import os,math,re

class Yinliang(): #设置系统音量

    # 整数的四舍五入
    def l_45(self,ints):

        ints , new= int(ints),10
        #取最后一个值
        have = int(str(ints)[-1:])
        if have >=5:
            ints -= have
            ints += 10
        else: ints -= have
        return ints

    def main(self,size_txt):
        try:
            #自定义声音时size_txt为字符串类型
            if type(size_txt) is str : txt = int(size_txt)
            else: txt  = self.l_45(size_txt)

            if txt >=20 and txt <=100:
                #y = 24.979ln(x) - 14.581
                y = 24.979*math.log(txt) - 14.581
                os.system("sudo amixer set Speaker {}%".format(y))
                return {'state':True,'data': "声音{}%".format(txt),'msg':'参数1，需要输入字符串类型！'}

            elif txt <20:
                y2 = 24.979*math.log(20) - 14.581
                os.system("sudo amixer set Speaker {}%".format(y2))
                return {'state':True,'data': "声音最小了",'msg':'参数1，需要输入字符串类型！'}

            elif txt >100:
                y3 = 24.979*math.log(100) - 14.581
                os.system("sudo amixer set Speaker {}%".format(y3))
                return {'state':True,'data': "声音最大了",'msg':'参数1，需要输入字符串类型！'}

        except:return {'state':True,'data': "没听清你说声音设置多少呢",'msg':'参数1，需要输入字符串类型！'}

class Voices():  #分析是否控制音量的语句

    def chushizhi(self):
        jieguo,jiance=str(),'['
        huoqu_os=os.popen("sudo amixer scontents | grep 'Front Left: Playback'|grep 'dB'").read()
        for x in re.sub(r'^.*k','',re.sub(r'].*$','',huoqu_os[len(re.sub(r'F.*$','',huoqu_os)):])):
            if x==jiance:
                jiance="kaishi"
            elif jiance=="kaishi":
                jieguo+=x
        #通过y = 1.7972e^(0.04x) x为填入的音量，y为实际音量 这个公式计算出实际音量。
        return 1.7972 * math.pow(2.718,0.04 * int(jieguo[:-2]))


    def __luiji_xing(self,txt):#模拟音量最大

        if txt   == '最大' : return 100
        elif txt == '最小' : return 20
        elif txt == '大点' : return self.chushizhi() + 10
        elif txt == '小点' : return self.chushizhi() - 10
        else:return txt

    def main(self,txt):
        return Yinliang().main(self.__luiji_xing(txt))

    #声音最大
    def voice_max(self,name):
        return Voices().main("最大")
    #声音最小
    def voice_mini(self,name):
        return Voices().main("最小")
    #声音大点
    def voice_larger(self,name):
        return Voices().main("大点")
    #声音大点
    def voice_small(self,name):
        return Voices().main("小点")
    #声音自定义
    def voice(self,name):
        # 取数字
        shuru = name['txt']
        ints = ''
        matchObj = re.findall( r'(\d+)', shuru, re.M|re.I)
        if len(matchObj)>0:ints = matchObj[0]
        return Voices().main(ints)

if __name__ == '__main__':
    '''
    dd={}
    for x in range(20,101):
        Yinliang().main(str(x))
        c = Voices().chushizhi()
        dd[c] = x
        print(x,"-->",c)
    print(dd)
    '''
    print(Voices().chushizhi())


