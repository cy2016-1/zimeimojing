# -*- coding: utf-8 -*-
from MsgProcess import MsgProcess
import time

class NowTime(MsgProcess):
    def Text(self, message):
        data = message["Data"]
        Triggers_time = ["现在时间", "几点","时间","现在几点"]
        Triggers_date = ["今天什么日子","今天日期","今年是","今天是","今天几","今天星期"]

        if [x  for x in Triggers_time if x in data ]:
            # 凌晨：0-5
            # 早上：5-11
            # 中午：11-13
            # 下午：13-17
            # 傍晚：17-19
            # 晚上：19-24
            obtain = int(  time.strftime("%H", time.localtime())   )
            if obtain in [1,2,3,4]:
                self.say( time.strftime("凌晨%H点%M分", time.localtime()) )
            if obtain in [5,6,7,8,9,10]:
                self.say( time.strftime("早上%H点%M分", time.localtime()) )
            if obtain in [11,12]:
                self.say( time.strftime("中午%H点%M分", time.localtime()) )
            if obtain in [13,14,15,16]:
                self.say( time.strftime("下午{0}点%M分".format(obtain-12), time.localtime()) )
            if obtain in [17,18]:
                self.say( time.strftime("傍晚{0}点%M分".format(obtain-12), time.localtime()) )
            if obtain in [19,20,21,22,23,0]:
                self.say( time.strftime("晚上{0}点%M分".format(abs(obtain-12)), time.localtime()) )

        elif [x  for x in Triggers_date if x in data ]:
            date=["天","一","二","三","四","五","六"][ int( time.strftime("%w", time.localtime())) ]
            self.say( time.strftime("%Y年%m月%d日星期{0}".format(date), time.localtime()) )

        self.Stop()

