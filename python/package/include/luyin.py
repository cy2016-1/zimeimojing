# -*- coding: utf-8 -*-

class Luyin():

    '''录音类'''

    def success(self,results):
        pass

    def error(self):
        pass

    '''
    录音主函数
    参数：
        Location -- 录音保存文件
        Stop_time -- 录音时长（秒）
        p_self -- 主进程对象（可提高代码运行效率）
    '''
    def main(self,Stop_time, p_self):

        #print("录音")
        p_self.sw.sendmic('start')
        p_self.sw.sendmic('open')
        frames  = []
        on1     = p_self.time.time()
        micmax  = []#声音最大值
        delayed = 0 #延时
        while 1:
          #  print('begin ')
            p_self.sw.sendmic('1')
            data = p_self.stream.read(p_self.CHUNK,exception_on_overflow = False)
            frames.append(data)
            audio_data = p_self.np.fromstring(data, dtype=p_self.np.short)
            temp = p_self.np.max(audio_data)
            on2 = p_self.time.time()
            #录音最低时间
            mictime = on2 - on1
            if mictime <2:
                micmax.append(temp)
                #假设得到全部的最大值5个
                #每个除以5
                #在除以2
                #得到前面2秒的平均/2分贝 == 动态伐值
                micstop = (sum(micmax)/len(micmax))/2

                continue


            if mictime > 5 :
              #  print("最大时间到了")
                break
            #自动检测分贝和最少时间
            if temp < micstop and mictime >=2:
                p_self.time.sleep(0.01)
                delayed +=1
                #print(delayed)

            #加最后1秒静音就停止
            if delayed >=15 :
              #  print("检测到信号")
             #   print('当前阈值：',temp)
                break

            p_self.sw.sendmic('0')

        p_self.sw.sendmic('close')
        p_self.stream.stop_stream()
        p_self.stream.close()
        p_self.p.terminate()
        p_self.sw.sendmic('stop')

        self.success( b''.join(frames) )



if __name__ == '__main__':
    Luyin().main("recording.wav",10)