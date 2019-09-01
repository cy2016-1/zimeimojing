import importlib,os,re,sys
from package.base import Base,log
import multiprocessing as mp                            #多进程
import psutil
import ast

#技能处理类
class Function(Base):

    def __init__(self):
        self.pid_file = os.path.join(self.config['root_path'], 'runtime/plugin_pid')
        if os.path.isfile(self.pid_file) is False:
            os.mknod(self.pid_file)

    #开始运行：长驻插件
    def Run_StayPlugin(self, command_success, public_obj, name_ ):

        def run_plugin(command_success, public_obj, name_ ):
            log.info('开始运行插件')

            modular  = importlib.import_module(name_["modular"])
            class_   = getattr(modular,name_["class"])
            class_in = class_(public_obj)

            #插件进入
            load     = getattr(class_in,'load')
            ret_dict = load(name_)

            #插件暂停
            pause    = getattr(class_in,'pause')

            #插件继续
            resume   = getattr(class_in,'resume')

            #插件结束执行
            unload   = getattr(class_in,'unload')
            unload   = command_success
            #ret_dict['type'] = 'system'
            #unload(ret_dict)
            '''
            while 1:
                str1 = public_obj.plugin_conn.recv()
                print('管道通知:', str1 )
                if str1:
                    str1 = ast.literal_eval(str1)
                    print( str1 )
                    if 'state' in str1.keys():
                        pause()
                    else:
                        resume()
            '''

        #进入的进程名称
        en_pname = name_["class"]

        p_id = ''
        with open(self.pid_file,'r', encoding='utf-8') as of:
            p_id = of.read()

        is_run = False
        if p_id:
            [pid,pname] = p_id.split('|')

            try:
                pro = psutil.Process( int(pid) )
                if pro:       #进程存在
                    if str(pname)==str(en_pname):
                        is_run = True
                        #正在运行的插件与即将启动的进程名一样
                        public_obj.master_conn.send(name_)      #发送第二次启动指令
                    else:
                        #停止进程下所有子进程
                        for x in pro.children():
                            pid_arr = re.findall(r'pid\=(\d+)', str(x), re.M|re.I)
                            if pid_arr:
                                os.system('sudo kill -9 '+ str(pid_arr[0]) )

                        os.system('sudo kill -9 '+ pid)
                        pro.terminate()       #结束当前进程
            except:
                print('没找到进程')

        if is_run is False:
            pub = mp.Process(
                target = run_plugin,
                name = name_["class"],
                args = (command_success, public_obj, name_)
            )
            pub.start()

            print('============='*6)
            print( pub.name, pub.pid )
            print('============='*6)

            with open(self.pid_file,'w',encoding='utf-8') as of:
                of.write(str(pub.pid)+'|'+str(pub.name))


    #入口函数
    '''
        public_obj  --  全局类对象
        name_       --  json 格式消息体
    {"state": 布尔类型 , "txt":原始字符串,"cmd":指令,"modular":模块,"class":类,"def":方法}
    '''
    def main(self, command_success, public_obj, name_):
        log.info('进入技能处理类:Function.main')
        ret_json = {'state':False,'data':'对不起！我未能完成您的指令。','type':'system','msg':'功能插件出错'}

        print('---------------'*6)

        #取得插件配置文件内容 - Start
        plugin_root = name_['modular']
        plugin_root = re.sub(r'\.', "/", plugin_root)
        conf_file = os.path.join(self.config['root_path'], plugin_root +'.conf')

        print(conf_file)
        conf_json = ''
        if os.path.isfile(conf_file):
            with open(conf_file,'r', encoding='utf-8') as of:
                conf_json = of.read()

        conf_dict = {}
        if conf_json:
            conf_dict = ast.literal_eval(conf_json)
            print( conf_dict )

        if len(conf_dict)>1:
            if conf_dict['type']=='stay':       #长驻内存插件
                self.Run_StayPlugin(command_success, public_obj, name_)

        #取得插件配置文件内容 - End

if __name__ == '__main__':
    pass
    #print(Function().main( {"state": True ,"txt": '' ,"ints":'', "def":'cloes_screen',"modular":'package.include.skills.action.screens',"class":"Screen"}))