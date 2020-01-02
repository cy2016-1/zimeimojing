from package.base import Base,log
from plugin import Plugin
import package.include.visual as visual
import multiprocessing as mp  # 多进程

#启动人脸识别 识别摄像头前面是谁
class My(Plugin,Base):

    def __init__(self, public_obj ): 
       
        self.public_obj  = public_obj 
        
    #结果   
    def success(self,data):
    
        if data:
            #改变全局用户id
            self.public_obj.uid.value = int(data["body"]['uid'])                  
            self.public_obj.master_conn.send({'optype': 'return','type': 'system','state': True,'msg': '人脸识别','data':data["data"],'stop':True} ) 
        else:
            #识别不出  改变全局用户id为默认
            self.public_obj.uid.value = 0 
            self.public_obj.master_conn.send({'optype': 'return','type': 'system','state': True,'msg': '人脸识别','data':"不知道呢",'stop':True} )     
               
    
    def main(self):
    
        self.visual = visual.Visual()
        self.visual.success =self.success
        self.visual.main()        
        
     #启动
    def start(self,x):
    
        m = mp.Process(target =self.main )
        m.start()
