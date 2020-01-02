import webrtcvad
import ctypes
import struct
import time,os
from package.base import Base,log

class RecS16le16kC1:
    def __init__(self, path=r'./S16leR16kC1.so'):
        self.libso = ctypes.cdll.LoadLibrary(path)
        if not ctypes.c_bool(self.libso.init()).value:
            raise 'Library S16leR16kC1.init() failed !'
        addr = ctypes.string_at(self. libso.buffersize, 4)
        self.buffersize = struct.unpack('I', addr)[0]
        log.info('Python read from dll buffersize = ', self.buffersize)

    def read(self):
        self.libso.readsound.argtypes = [ctypes.c_char_p]
        self.libso.readsound.restype = ctypes.c_bool
        data = ctypes.create_string_buffer(self.buffersize)
        ret = ctypes.c_bool(self.libso .readsound(data))
        if not ret.value:
            log.info("Recording XRUN ERROR .")
        return data

    def close(self):
        self.libso.closesound()



class Luyin(Base):
    '''录音类'''

    def success(self,results):
        pass

    def error(self,bug):
        print(bug)

    def is_speech(self, buffer):
        # 检测长度为size字节的buffer是否是语音

        size = len(buffer)
        RATE = 16000
        assert size >= 320  # 长度不能小于10ms
        if size < 640:
            return self.vad.is_speech(buffer[0:320], RATE)
        score = 0
        blocks = size // 640  # 将音频分割
        for i in range(blocks):
            score += self.vad.is_speech(buffer[i*640:(i+1)*640], RATE)
        return score / blocks

    def main(self, Stop_time, public_obj):
        streamrec = RecS16le16kC1(os.path.join(self.config['root_path'],"bin/S16leR16kC1.so"))
        self.vad = webrtcvad.Vad(0)
        rec = []
        no_speechtime = 0
        rectime = time.time()
        public_obj.sw.sendmic('start')

        while((time.time() - rectime) <= Stop_time):           
            public_obj.sw.sendmic(1)
            data = streamrec.read()
            rec.append(data)
            if self.is_speech(data) > 0.2:
                no_speechtime = 0
                public_obj.sw.sendmic(0)
                continue
            elif no_speechtime == 0:
                no_speechtime = time.time()
            if time.time() - no_speechtime > 0.5 and (time.time() - rectime) > 1.5:
                break
        public_obj.sw.sendmic('stop')

        writetofile = rec[0:-3]
        writetofile = b"".join(writetofile)
        streamrec.close()
        self.success(writetofile)  # 回调

  

if __name__ == "__main__":
    # 录音样例 5秒
    rec = RecS16le16kC1()  # 1 创建录音对像
    with open('sound.pcm', 'wb') as f:
        for i in range(40):
            data = rec.read()  # 2 直接读即可
            f.write(data)
    rec.close()  # 3 关闭音频对像


