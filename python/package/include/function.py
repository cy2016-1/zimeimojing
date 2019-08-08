import importlib

#技能处理类
class Function():

    #入口函数
    '''
        public_obj  --  全局类对象
        name_       --  json 格式消息体
    {"state": 布尔类型 , "txt":原始字符串,"cmd":指令,"modular":模块,"class":类,"def":方法}
    '''
    def main(self, public_obj, name_):
        ret_json = {'state':False,'data':'对不起！我未能完成您的指令。'+name_["def"],'type':'system','msg':'功能插件出错'}

        if name_["def"] :

            try:
                modular  = importlib.import_module(name_["modular"])
                class_   = getattr(modular,name_["class"])
                def_     = getattr(class_(public_obj),name_["def"])
                ret_dict = def_(name_)

                ret_dict['type'] = 'system'
                if ret_dict['state']==True:
                    ret_json = ret_dict
                del modular,class_,def_,ret_dict
                return ret_json

            except: return ret_json

        else:
            return ret_json


if __name__ == '__main__':
    pass
    #print(Function().main( {"state": True ,"txt": '' ,"ints":'', "def":'cloes_screen',"modular":'package.include.skills.action.screens',"class":"Screen"}))