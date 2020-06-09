import package.paho.mqtt.client as mclient
from MsgProcess import MsgProcess, MsgType
import json
import os
import logging
import re
import copy


class MqttProxy(MsgProcess):
    '''
    MQTT代理，接受从微信或网页发来MQTT消息，再转发给相关的服务插件。
    对插件或其它模块来说是透明的
    '''

    def __init__(self, msgQueue):
        super().__init__(msgQueue)
        self.isconnect = False
        warp_path = self.config["MQTT"]["warp"]
        file = os.path.join(warp_path,"topic.json")
        with open(file) as f:
            topic = json.load(f)
        self.subscribe = topic["subscribe"]
        self.pubscribe = topic["pubscribe"]

        file = os.path.join(warp_path,"send.json")
        with open(file) as f:
            self.sendwarp = f.read()

        file = os.path.join(warp_path,"receive.json")
        with open(file) as f:
            self.receivewarp = f.read()

        self.plugintemp = {}
        template_path = r'./data/conf/pluginconfig.json'
        with open(template_path) as f:
            self.plugintemp = json.load(f)

    def Start(self, message):
        if not self.isconnect:         
            self.isconnect = True
            self.getConfig()
            mqtt_conf = self.config['MQTT']
            self.__host = mqtt_conf["server"]            # mqtt.16302.com
            self.__port = int(mqtt_conf["port"])         # 1883
            self.__clientid = mqtt_conf["clientid"]      # 设备id
            self.__mqtt_name = mqtt_conf["mqttname"]     # 用户名
            self.__mqtt_pass = mqtt_conf["mqttpass"]      # 密码
            self.client = mclient.Client(client_id=self.__clientid)
            self.client.username_pw_set(self.__mqtt_name, self.__mqtt_pass)
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client_connect()

    def Text(self, message):
        ''' 回调函数,收到插件发来的文本消息 转发到mqtt服务器 '''
        plugin = message['Sender']
        Data = message['Data']
        
        Data = json.dumps(Data)
        jsonText = self.sendwarp.replace(r'%plugin%', plugin)
        jsonText = jsonText.replace(r'%data%', Data)
        jsonText = json.loads(jsonText)

        for pub in self.pubscribe:
            topic = pub.replace(r'%clientid%', self.__clientid)

            self.publish(topic, json.dumps(jsonText, ensure_ascii=False))
            logging.debug('MQTT SEND topic:%s %s' % (topic, jsonText))

    # 加载插件列表
    def load_pugin_list(self, data):
        pluginpath = r'./plugin'

        send_json = {}
        if data['type'] == 'getlist':
            plugin_list = []
            for filedir in os.listdir(pluginpath):
                if os.path.isdir(os.path.join(pluginpath, filedir)) and filedir != '__pycache__':
                    template_json = copy.deepcopy(self.plugintemp)          # 拷贝一个对象

                    json_file = os.path.join(pluginpath, filedir, 'config.json')
                    with open(json_file, 'r') as f:
                        config_json = json.load(f)

                        template_json.update(config_json)
                        plugin_list.append(template_json)

            send_json = {
                "Sender": "equipm",
                "Data": {
                    "action": "PLUGIN_LIST",
                    "list": plugin_list
                }
            }
        elif data['type'] == 'getinfo':
            filedir = data['pugin'] + '/'
            template_json = copy.deepcopy(self.plugintemp)          # 拷贝一个对象
            json_file = os.path.join(pluginpath, filedir, 'config.json')
            plugin_info = {}
            with open(json_file, 'r') as f:
                config_json = json.load(f)

                template_json.update(config_json)
                plugin_info = template_json

            if len(plugin_info) > 0:
                send_json = {
                    "Sender": "equipm",
                    "Data": {
                        "action": "PLUGIN_INFO",
                        "info": plugin_info
                    }
                }
        if len(send_json) > 0:           
            self.Text(send_json)

    def client_connect(self):
        self.client.connect_async(self.__host, self.__port, 60)  # 非阻塞模式
        self.client.loop_start()  # 非阻塞模式

    # 连接成功回调
    def on_connect(self, client, userdata, flags, rc):
        logging.info('mqtt开始订阅主题.')

        for sub in self.subscribe:
            topic = sub.replace(r'%clientid%', self.__clientid)

            logging.info("subscribe topic: %s" % topic)
            self.client.subscribe(topic)

        logging.info('mqtt完成主题订阅.')
           
    # 收到消息回调
    def on_message(self, client, userdata, msg):
        """收到mqtt消息，转发到插件 根据消息类型分析"""
        magstr = msg.payload.decode("utf-8")
        logging.debug('MQTT RECEIVE: %s' % magstr)

        json_obj = self.receivewarp.replace(r'%data%', magstr)
        json_obj = json.loads(json_obj)

        if type(json_obj) is dict and 'receive' in dict(json_obj).keys():
            logging.info(json_obj)
            if str(json_obj['receive']) == 'equipm':  # 接收端是树莓派设备
                # 2.0方法 mqtt协议新字典,只要传送激活词就可以激活任意插件
                # {sender:'发送方', 'receive':'equipm', 'plugin':插件名, data='激活词'}
                Data = json_obj['data']
                if 'plugin' in dict(json_obj).keys():
                    pluginReceiver = json_obj['plugin']
                    self.send(MsgType=MsgType.Text, Receiver=pluginReceiver, Data=Data)                    
                    self.send(MsgType=MsgType.LoadPlugin, Receiver='ControlCenter', Data=pluginReceiver)
                    return
                elif type(Data) is dict:
                    if 'action' in dict(Data).keys() and Data['action'] == 'PLUGIN_LIST':
                        self.load_pugin_list(Data)
                        return

    # 发布消息
    def publish(self, topic, msgbody):
        self.client.publish(topic, msgbody, qos=2)
