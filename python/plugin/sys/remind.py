# -*- coding: utf-8 -*-
from plugin import Plugin

#提醒插件
class Remind(Plugin):

    def __init__(self, public_obj ):
        super().__init__( public_obj )
        print('提醒插件已经启动')

    #插件开始
    def start(self, sbobj={}):
        print( sbobj )