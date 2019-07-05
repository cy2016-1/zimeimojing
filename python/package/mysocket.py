from websocket import create_connection
import json

class Mysocket():
    """内部通信模块"""

    def __init__(self ):
        print("内部通信已经初始化")

    def connection(self):
        try:
            self.ws = create_connection("ws://localhost:8103")
        except Exception as e:
            self.ws = False

    #重新连接
    def reconnect(self):
        print('重新连一下')
        try:
            self.ws = self.ws.connect("ws://localhost:8103")
        except Exception as e:
            self.ws = False


    #发送屏幕文字
    def send_info(self, txt= {}):
        if self.ws:
            info = {
                'init':0,
                'obj':'mojing',     # 对象： zhuren / mojing  主人/魔镜
                'emot':'',          # 情感：
                'msg': txt['msg'],  # 消息体
                'timer':3           # 停留时长（秒）
            }
            if type(txt['obj']) is str:
                info['obj'] = txt['obj']

            if 'emot' in txt.keys():
                info['emot'] = txt['emot']

            if 'init' in txt.keys():
                info['init'] = txt['init']

            info['timer'] = round(len(txt['msg']) * 0.21, 2)

            jsonstr = json.dumps(info)
            self.ws.send(jsonstr)

    #发送麦的状态
    def sendmic(self, sendstr= ''):
        if self.ws:
            self.ws.send('{"m":"'+str(sendstr)+'"}')

    #接收消息
    def recv(self):
        result =self.ws.recv()
        return result

    #连接初始化
    def init(self):
        self.connection()

    def close(self):
        self.ws.close()