# -*- coding: UTF-8 -*-
#import package.config as config
from package.base import Base
import os,threading,re,string,math,time,json
import multiprocessing as mp    #创建进程

class Task(Base):
    """计划任务类"""

    def __init__(self):
        pass


    #运行任务
    def execTask(self, execarr):
        cmd = execarr['exeurl'];
        urltype = str(execarr['urltype']);
        logfile = self.config['root_path']+'/runtime/log/'+ time.strftime("%Y-%m-%d", time.localtime()) +'.log';

        log = '\r\n【'+time.strftime("%H:%M:%S",time.localtime())+'】'+cmd;
        output = os.popen(cmd).read()
        log += "\r\n"+output+"\r\n";
        self.file_put_contents(logfile, log);

    #创建线程
    def createFork(self, taskarr ):
        #创建线程函数
        class myThread(threading.Thread):
            def __init__(self, threadID, name, counter):
                threading.Thread.__init__(self)
                self.threadID = threadID
                self.name = name
                self.counter = counter
            def run(self):
                #print ("开始线程：" + self.name)
                Task().execTask(self.counter)
                #print ("退出线程：" + self.name)

        #print(taskarr)
        if len(taskarr)>0 :
            #print('有任务')
            for task in taskarr:
                #print(task)
                myThread( task['id'], task['name'], task ).start()


    #格式化判断语法替换
    def strtr(self, form, datearr):
        for x in datearr:
            form=form.replace(x,str(datearr[x]))
        form=form.replace("||"," or ");
        form=form.replace("&"," and ");
        return form;

    #格式化判断语法
    def hzf_formatdate(self, format, date ):
        date = time.localtime(date);
        forarr={}
        forarr['Y'] = time.strftime("%Y",date);		#年
        forarr['n'] = int(time.strftime("%m",date));		#月
        forarr['j'] = int(time.strftime("%d",date));		#日
        forarr['w'] = time.strftime("%w",date);		#星期
        forarr['G'] = int(time.strftime("%H",date));		#小时 H
        forarr['i'] = int(time.strftime("%M",date)); 	#分钟
        forarr['s'] = int(time.strftime("%S",date)); 	#秒
        return self.strtr(format,forarr);

    def file_put_contents(self, filename, wstr='' ):
        fo = open(filename, "a+")
        fo.seek(0, 2)
        fo.write( str(wstr) )
        fo.close()

    #启动任务
    def start_task(self, config ):
        with open(config['root_path']+'/data/tasks.json', 'r',encoding='UTF-8') as f:
            data = json.load(f)
            while True:
                item = iter(data)    # 创建迭代器对象
                today = time.strftime("%Y-%m-%d", time.localtime())
                nts = int(time.time())
                exec_tasks = []
                #print("当前时间:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(nts)))
                for li in item:
                    #print(li['name'])
                    if li['kaiguan']==0 or li['exeurl']=='':continue;
                    begin = time.mktime(time.strptime(today+' '+li['begin'], "%Y-%m-%d %H:%M:%S"));
                    end = time.mktime(time.strptime(today+' '+li['end'], "%Y-%m-%d %H:%M:%S"));
                    if nts > begin and nts < end:
                        run_str = self.hzf_formatdate( li['condition'], nts )
                        yn = eval(run_str);
                        if yn:
                            exec_tasks.append({'id':li['id'],'name':li['name'],'exeurl':li['exeurl'],'urltype':li['urltype']});
                #print(exec_tasks);
                time.sleep(1)
                self.createFork(exec_tasks);     #创建线程

    def main(self):
        p2 = mp.Process(
            target = self.start_task,
            args = ( self.config, )
        )
        p2.start()

'''====================【任务分配开始】==================='''
'''
if __name__ == '__main__':
    TASK_NAME = __file__
    TASK_PATH = os.path.dirname(TASK_NAME);
    taskcmd='ps ax | grep ' + TASK_NAME
    out = os.popen(taskcmd).read(); # 检测是否已经运行
    pat = re.compile(r'.+(\/python\d?\s+'+TASK_NAME+')')
    res = pat.findall(out)
    if len(res)>1:
        print('\033[31m任务已经在运行，可以使用\033[0m \033[32m'+taskcmd+'\033[0m \033[31m命令查询核实\033[0m')
    main()
'''