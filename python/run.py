#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os,sys,re,time
import multiprocessing as mp        #多进程

this_path = os.path.dirname(os.path.dirname(__file__))

task_main       = 'main.py'                         #后端任务
task_main_cmd   = os.path.join(this_path,'python/'+task_main)

task_mojing     = 'moJing'                          #前端任务
task_mojing_cmd = os.path.join(this_path,'app/'+task_mojing)   #前端任务
task_run        = os.path.basename(__file__)        #监控任务

logfile = os.path.join(this_path,'python/runtime/log/tasks.log')	# 日志文件

#停止任务
def stop( task_name ):
    taskcmd = 'ps ax | grep ' + task_name
    out = os.popen(taskcmd).read();               # 检测是否已经运行
    pat = re.compile(r'(\d+).+('+task_name+')')
    res = pat.findall(out)
    for x in res:
        pid = x[0]
        cmd = 'sudo kill -9 '+ pid
        out = os.popen(cmd).read()
    print('[\033[31m停止\033[0m] 任务成功！')

#查询任务
def ps_ax( task_name ):
    taskcmd = 'ps ax | grep ' + task_name
    out = os.popen(taskcmd).read();               # 检测是否已经运行
    pat = re.compile(r'(\d+).+('+task_name+')')
    res = pat.findall(out)
    if len(res)>2:
        return True
    else:
        return False

def start(run_file, cmdtype ='system'):
    cmd = 'export DISPLAY=:0 && '+ run_file
    if cmdtype == 'system':
        os.system(cmd)
    else:
        os.popen(cmd)


#启动Python
def start_python( argv ):
    while True:
        is_task_main = ps_ax(task_main)
        if is_task_main == False:
            start('sudo '+task_main_cmd, 'system')
        time.sleep(3)

#启动Mojing前端
def start_mojing_app( argv ):
    while True:
        is_task_mojing = ps_ax(task_mojing)
        if is_task_mojing == False:
            start(task_mojing_cmd, 'system')
        time.sleep(3)

if __name__ == '__main__':
    if len(sys.argv)>1:
        argv = sys.argv[1]
    else:
        argv = ""

    if argv == 'stop':
        stop(task_main)
        stop(task_mojing)
        stop(task_run)
    elif argv == 'restart':
        stop(task_main)
        stop(task_mojing)

    #检测自己有没有运行
    runcmd = 'ps ax | grep ' + task_run
    out = os.popen(runcmd).read();               # 检测是否已经运行
    pat = re.compile(r'(\d+).+(\/python\d?\s+\S+'+task_run+')')
    runres = pat.findall(out)
    if len(runres) > 1:
        exit()

    app_p = mp.Process(
        target = start_mojing_app,
        args = (argv,)
    )
    app_p.start()

    main_p = mp.Process(
        target = start_python,
        args = (argv,)
    )
    main_p.start()
