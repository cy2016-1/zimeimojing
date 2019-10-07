# -*- coding: utf-8 -*-
import json
import re
import string
import urllib.request
from urllib.parse import urlencode

import jwt
from package.base import Base, log
from plugin import Plugin


class Tuling(Base,Plugin):

    def __init__(self, public_obj ):
        self.payload = {
            'APPID' :'kWf7I8VjBre1BXP',
            'TOKEN' : 'o2GQF8Ri73Crcn9WiGH8X3K4e6huGb',
            'EncodingAESKey' : '2uetECGe8oob6bbSvLj4DBNjPh2epX1y8mws0pENF5g'
        }

        self.apiUrl  =  'https://openai.weixin.qq.com/openapi/message/'

    '''
    main# 对外调用接口
    '''
    def start(self,name):
        try:
            if type(name) is not dict:
                return {'state':False,'data': '我不知道你说了啥','type':'system', 'msg':'参数1，需要输入图灵交流的文字。字符串类型！'}


            header = {"username":"小美","msg":name['data']}

            headers = {'alg': "HS256"}
            query = jwt.encode(header, self.payload['EncodingAESKey'],algorithm=headers['alg'],headers=headers).decode('ascii')

            url = self.apiUrl + self.payload['TOKEN']

            post_json = {"query":query}
            post_json = urlencode(post_json).encode('utf-8')
            
            page = urllib.request.urlopen(url,data=post_json, timeout = 25)      #响应时间定为了25秒

            #判断网络请求成功
            if page.getcode() == 200:
                html = page.read().decode("utf-8")
                #判断返回数据是否是字典,可能返回的是数字所以str
                if re.sub( r'{.*}', "", str(html)) == "":
                    res = json.loads(html)

                    #删除字典内容和网址
                    if res['answer_type']=='text':
                        data = res['answer']
                    else:
                        data = res['ans_node_name'] + '功能尚未启用'

                    if data == '': data = "不知道"
                    del res,page,url,html
                    return {'state':True,'data':data ,'type':'tuling','msg':'对话机器人回复成功！'}
                else:
                    return {'state':False,'data':'我想不出来。','type':'system','msg':'服务器返回的不是字典！'}
            else:
                return {'state':False,'data':'网络可能有点问题，请检查一下网络哦。','type':'system','msg':'请求失败！'}
        except Exception as bug:
            log.warning('对话机器人超时',bug)
            return {'state':False,'data':'网络可能有点问题，需要检查一下网络。','type':'system','msg':'连接对话机器人服务器超时！'}

if __name__ == '__main__':


    print( Tuling().main('520'))
