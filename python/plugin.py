#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import sys
from plugin import ddns,nmap

if len(sys.argv)>1:
    argv = sys.argv[1]

    if (argv=='nmap'): nmap.main()      #扫描家人
    if (argv=='ddns'): ddns.main()      #动态域名
