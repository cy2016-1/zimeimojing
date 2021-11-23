from MsgProcess import MsgProcess, MsgType
from multiprocessing import Queue

class SayIp(MsgProcess):
    def __init__(self, msgQueue):
        super().__init__(msgQueue)

    def Text(self, message):
        self.say(message)

SayIp(Queue()).Text('您好，世界！')