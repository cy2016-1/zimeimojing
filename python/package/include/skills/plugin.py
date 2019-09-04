class Plugin():
    def __init__( self, public_obj ):
        self.public_obj = public_obj

    #插件开始
    def load(self, sbobj):
        pass

    #插件等待（暂时停止）
    def pause(self):
        print('执行了暂停---------'*3)
        pass
        #return self.public_obj.os_api("voice_arousal")

    #插件继续
    def resume(self):
        print('执行插件继续---------'*3)
        pass
        #return self.public_obj.os_api("sound_change")

    #插件结束
    def unload(self, enobj ):
        print('-'*100)
        print(enobj)
        print('-'*100)
        return False
