#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import package.task as task         #计划任务
import package.check as check       #设备检测模块
import package.master as master     #主控制
if __name__ == '__main__':

    #启动：计划任务
  #  task.Task().main()

    #启动检测模块
    check.Check().main()

    #启动：主控制
    master.Master().main()