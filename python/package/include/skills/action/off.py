import re
class Off():

    def main(self,name):
        if re.search(name["cmd"],name["txt"]).span()[0] == 0:
            return {'state':True,'data': "好的,如果有需要记得再次呼唤我",'msg':'参数1，需要输入字典类型！','stop':True}
