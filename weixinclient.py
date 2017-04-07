#!/usr/bin/env python
from wxpy import *

class WeiXinClient:
    
    def __init__(self,tag):
        self.bot = None
        self.master = None
        self.heartbeat_dict={}
        self.tag = tag

    def start(self):
        self.bot = Bot(cache_path=True)
        self.master = self.bot.groups().search('机器人')[0]

        #@self.bot.register(self.master)
        #def handle_msg(message):
        #    pass


    def stop(self):
        if self.bot != None:
            self.bot.logout()

    def sendDeal(self,deal):
        print("send Deal")
        if self.master != None:
            self.master.send('成交 %s %s %s %s %s'%(deal.user,deal.time,deal.instrument,deal.price,deal.holders))
            
    def sendTimeBarInfo(self,timebarinfo):
        print("send timebarinfo")
        if self.master != None:
            self.master.send('均值 %s--%s:%s %s'%(timebarinfo.user,timebarinfo.time,timebarinfo.instrument,timebarinfo.price))

    def sendHeartBeat(self,heartbeat):
        print("send heartbeat")
        self.heartbeat_dict[heartbeat.user] = heartbeat.timestamp

    def sendWarnHeartBeat(self,heartbeat,OK):
        print("send warn heartbeat")
        if OK:
            msg = "OK"
        else:
            msg = "Error"
        if self.master != None:
            self.master.send('%s-- last heartbeat %s %s'%(heartbeat.user,heartbeat.timestamp,msg))

    
