# -*- coding: utf-8 -*-
# @Date: 2019-12-26 09:35:35
# @LastEditTime: 2020-01-22 14:32:04
# @Description: 屏幕显示的消息进程，只要实现Text消息响应即可。

import json
import logging
import re
import time
from threading import Thread

from python.bin.SocketScreen import SocketScreen
from MsgProcess import MsgProcess, MsgType

class Screen(MsgProcess):
    def __init__(self, msgQueue):
        super().__init__(msgQueue)
        self.sw = SocketScreen()

    # 收到消息回调
    def on_message(self, client, server, message):
        try:
            mess = json.loads(message)
            if type(mess) is dict:
                if 'MsgType' not in mess.keys():
                    mess['MsgType'] = 'Text'
                mess['MsgType'] = re.sub(r'MsgType\.','', mess['MsgType'])
                if not hasattr(MsgType, str(mess['MsgType'])):
                    mess['MsgType'] = 'Text'
                new_msgtype = MsgType[ mess['MsgType'] ]
                self.send(MsgType = new_msgtype, Receiver = mess['Receiver'], Data = mess['Data'])
        except json.JSONDecodeError:
            self.send(MsgType = MsgType.Text, Receiver = 'ControlCenter', Data = message)
        except:
            pass

    # 有新的前端屏幕接入
    def client_access(self, client, server):
        self.open_default()

    def client_disconnect(self, client, server):
        logging.info("屏幕%s已断开" % client['id'])

    # 启用屏幕通讯服务器
    def StartServer(self):
        self.sw.message_received = self.on_message
        self.sw.client_access = self.client_access
        self.sw.client_disconnect = self.client_disconnect
        p = Thread(target=self.sw.run)
        p.start()

    # 打开默认首页
    def open_default(self):
        index_url = self.config['VIEW']['path'] + self.config['VIEW']['index']
        nav_json = {
            'type': 'nav',
            'data': {
                "event": "index",
                "url": index_url
            }
        }
        self.send_data(nav_json)

    # 开启屏幕通信服务
    def Start(self, message):
        self.StartServer()

    # 处理文本消息
    def Text(self, message):
        Data = message['Data']

        # 如果Data 是字符串
        if isinstance(Data, str):
            info = {
                'type': 'text',
                'data': {
                    'init': 0,           # 是否为初始化唤醒
                    'obj': 'mojing',     # 对象： zhuren / mojing  主人/魔镜
                    'emot': '',          # 情感：
                    'msg': Data          # 消息内容
                }
            }
            if message['Sender'] == 'Record':  # 主人
                info['data']['obj'] = 'zhuren'

            self.send_data(info)
            return

        # 对Data词典解析
        if isinstance(Data, dict):
            self.send_data(Data)              # 用户自定义数据 直接发给前端

    #发送屏幕文字
    def send_data(self, Data):
        try:
            self.sw.on_send( json.dumps(Data) )
        except json.JSONDecodeError:
            logging.error('发送消息格式错误')
        except:
            pass

    def Stop(self, message=None):
        super().Stop(message)
