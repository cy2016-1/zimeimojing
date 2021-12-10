# @Date: 2020-03-17 15:33:10
# @LastEditTime: 2020-03-17 15:34:34
# @Description:  定制开发CNW
import os
import logging
import json
from MsgProcess import MsgProcess, MsgType
        
        
class CNW(MsgProcess):
    comfile = "语音命令.json"
    confile = "语音控制.json"

    def Text(self, message):
        data = message['Data']
        if isinstance(data, str):
            ''' 文本解析 语音控制发送到mqtt '''
            path = os.path.dirname(os.path.abspath(__file__))
            file = os.path.join(path, self.confile)
            try:
                with open(file) as f:
                    jsondit = json.load(f)                    
            except Exception as e:
                logging.error(e)
            for (cmdcode, worlds) in jsondit.items():                
                if any(map(lambda w: data in w, worlds)):
                    mqtt = {"命令编码": cmdcode, "命令内容": data}
                    self.sendmqtt(mqtt)
                    return
            msg = "无法识别的控制命令"
            logging.warning(msg)
            self.speak(msg)
            return
        
        if isinstance(data, dict):
            data = data['params']
            if "语音报告" in data.keys():
                self.speak(data["语音报告"])

            if "语音命令" in data.keys():
                num = str(data["语音命令"])
                path = os.path.dirname(os.path.abspath(__file__))
                file = os.path.join(path, self.comfile)
                try:
                    with open(file) as f:
                        jsondit = json.load(f)   
                        print(jsondit)        
                    command = jsondit[num]
                    print(command)   
                    self.send(MsgType.Text, Receiver="ControlCenter", Data=command)
                    logging.info(command)
                except Exception as e:
                    logging.error(e)
             
    def sendmqtt(self, data):
        self.send(MsgType=MsgType.Text, Receiver="MqttProxy", Data=data)

    def speak(self, data):
        self.send(MsgType=MsgType.Text, Receiver="SpeechSynthesis", Data=data)

