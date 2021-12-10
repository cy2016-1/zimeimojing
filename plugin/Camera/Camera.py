# -*- coding: utf-8 -*-

import os,re
from MsgProcess import MsgProcess, MsgType

        
class Camera(MsgProcess):
    def process(self):

        taskcmd = 'ps ax | grep raspistill' 
        out = os.popen(taskcmd).read()             
        pat = re.compile(r'(\d+).+(raspistill)')
        return pat.findall(out)


    def Text(self, message):  

        data =message["Data"]

        for x in self.process():
            os.system("sudo kill -9 {0} 2>/dev/null".format(x[0]))  

        if "打开" in data:
            os.popen("sudo raspistill -hf   -t 300000")
            self.Stop()  
            return 1

        if "黑白特效" in data:
            os.popen("sudo raspistill  -hf   -t 300000   -cfx  blackboard")
            self.Stop()  
            return 1
            
        self.Stop()  

