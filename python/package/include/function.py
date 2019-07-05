import importlib

class Function():

    def main(self,name_):
        ret_json = {'state':False,'data':'对不起！我未能完成您的指令。','type':'system','msg':'功能插件出错'}

        if name_["def"] :
            try:
                modular  = importlib.import_module(name_["modular"])
                class_   = getattr(modular,name_["class"])
                def_     = getattr(class_(),name_["def"])
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

    print(Function().main( {"state": True ,"txt": '' ,"ints":'', "def":'cloes_screen',"modular":'package.include.skills.action.screens',"class":"Screen"}))