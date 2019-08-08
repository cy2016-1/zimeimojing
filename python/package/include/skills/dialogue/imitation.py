class Imitation():

    def main(self,name):

        data = name["txt"][len(name["cmd"]):]
        if len(data) >= 2:return {'state':True,'data': data,'msg':'参数1，需要输入字典类型！'}
        else:return {'state':True,'data': "你想让我说什么?",'msg':'参数1，需要输入字典类型！'}





