import json
import os
import sys
from urllib import parse

from MsgProcess import MsgType
from python.package.Mylib import Mylib

class ApiBase():
    '''
    WebApi 基本类，所有具体操作需继承此类，基本已封装好常用的常量和变量
    self.query -- 为客户端请求参数
    '''

    def __init__(self, handler):
        self.mimetype = handler.mimetype
        self.command = handler.command

        if self.command=='OPTIONS':
            handler.send_content('', self.mimetype, 200)
            return

        self.query = {}
        if hasattr(handler, 'query'):
            query = handler.query
            if len(query)>0:
                argv_dict = self.__parse_parse_qs(query)
                if len(argv_dict) > 0:
                    for argv_item in argv_dict:
                        argv_dict[argv_item] = str(argv_dict[argv_item])
                    self.query = argv_dict
                del argv_dict

        self.config = Mylib.getConfig()  # 取全局配置
        self.handler = handler

    # 拆分web请求参数
    def __parse_parse_qs(self, query):
        argv_dict = {}
        for item in query.split('&'):
            if item.find("=") != -1:
                item_tab = item.split('=')
                argv_dict[item_tab[0]] = item_tab[1]
        return argv_dict

    # 发送字典类型的消息
    def __send_dict(self, dictobj):
        template = {"MsgType": '', "Receiver": '',"Data": ''}
        if len(template.keys() & dictobj.keys()) != 3:
            return '发送参数格式有误'
        else:
            Sender = 'WebServer'
            if 'Sender' in dictobj.keys():
                Sender = dictobj['Sender']
            message = {"MsgType": dictobj['MsgType'], "Receiver": dictobj['Receiver'], "Data": dictobj['Data'], "Sender": Sender}
            return self.handler.Sock.sendall(json.dumps(message).encode())


    # 与消息队列通信的函数
    def send(self, Msg_type, Receiver=None, Data=None, Sender=None):
        if isinstance(Msg_type, dict):
            # 如果是字典则不考虑后面的参数
            return self.__send_dict(Msg_type)
        elif isinstance(Msg_type, str):
            if not hasattr(MsgType, str(Msg_type)):
                # 不是消息类型，先按JSON字符串处理
                try:
                    dictobj = json.loads(Msg_type)
                    # 继续进行格式判断
                    return self.__send_dict(dictobj)
                except:
                    # 按一般字符串处理，默认发送到控制中心
                    message = {"MsgType": "Text", "Receiver": "ControlCenter", "Data": Msg_type, "Sender": "WebServer"}
                    return self.handler.Sock.sendall(json.dumps(message).encode())
            elif Receiver==None:
                return '接收者（Receiver）参数不能为空'
            elif Data==None:
                return '发送数据（Data）参数不能为空'
            else:
                if Sender==None:Sender = "WebServer"
                # 是消息类型写法
                message = {"MsgType": Msg_type, "Receiver": Receiver, "Data": Data, "Sender": Sender}
                return self.handler.Sock.sendall(json.dumps(message).encode())


    def main(self):
        data = '感谢使用自美人工智能系统'
        return data
