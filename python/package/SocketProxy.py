# -*- coding: utf-8 -*-
# @Date: 2019-12-26 09:35:35
# @LastEditTime: 2020-01-22 14:32:04
# @Description: Socket消息进程

import json
import logging
import re
import time
from threading import Thread

from python.bin.SocketServer import SocketServer
from MsgProcess import MsgProcess, MsgType

class SocketProxy(MsgProcess):

    def __init__(self, msgQueue):
        super().__init__(msgQueue)
        self.sock = 0
        self.StartServer()

    # 收到消息回调
    def on_message(self, response, sock):
        self.sock = sock
        try:
            mess = json.loads(response)
            if type(mess) is dict:
                if 'MsgType' not in mess.keys():
                    mess['MsgType'] = 'Text'
                mess['MsgType'] = re.sub(r'MsgType\.','', mess['MsgType'])
                if str(mess['MsgType']) not in MsgType.__members__:
                    mess['MsgType'] = 'Text'
                new_msgtype = MsgType[ mess['MsgType'] ]
                self.send(MsgType = new_msgtype, Receiver = mess['Receiver'], Data = mess['Data'])
        except:pass

    # 启用Socket服务器
    def StartServer(self):
        self.sw = SocketServer(('0.0.0.0',8183))
        p = Thread(target=self.sw.run, args=(self.on_message,))
        p.start()

    def Start(self, message):
        pass

    def Stop(self, message=None):
        super().Stop(message)
