from MsgProcess import MsgProcess, MsgType

# 创建新插件默认生成的标准模板
# 开发者可以根据此模板继续开发实现自己的功能
class {0}(MsgProcess):

    # 默认开始事件，如果设置插件为自动启动，则会在插件加载后运行此事件
    def Start(self, message):
        self.say("您好!{1}插件已经启动成功!")

    # 此为插件默认文本消息通讯接收函数, message 为接收到的消息体
    def Text(self, message):
        Data = message['Data']

        # 此触发词为系统自动生成，你可以修改成自己的触发词。注意需要将config.json配置文件中同步修改
        Triggers = "{2}"

        if Data.find(Triggers) >= 0:
            self.say('谢谢您，我收到了您的'+ Triggers + '祝福啦!')

