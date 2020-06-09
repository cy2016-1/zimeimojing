from MsgProcess import MsgProcess, MsgType


class GeneralSwith(MsgProcess):
    '''万能开关插件'''

    def Text(self, message):
        Data = message['Data']
        if isinstance(Data, dict) and Data['receive'] == 'system':
            # 这是万能开关传过来数据
            wnkg_data = Data['data']
            if wnkg_data['type'] == 'switch':
                if wnkg_data['state'] == 1:
                    self.say('灯已打开')
                elif wnkg_data['state'] == 0:
                    self.say('灯已关闭')

            if wnkg_data['type'] == 'dht':
                wnkg_data = Data['data']
                state = {'humidity': wnkg_data['state']['humidity']+'%', 'temperature': wnkg_data['state']['temperature']+'℃'}
                # self.say(state, False, 'MqttProxy')
                self.send(MsgType.Text, "MqttProxy", state)
        else:
            if Data[-1:] == '灯':
                self.switch(Data)

            elif Data[-2:] == '光感':
                self.light(Data)

            elif Data[-2:] == '温度':
                self.dhtfunc(Data)