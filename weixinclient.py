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
        self.master = self.bot.friends().search('谢哲')[0]

    def stop(self):
        if self.bot != None:
            self.bot.logout()

    def sendDeal(self,deal):
        print("send Deal")
        if self.master != None:
            self.master.send('deal %s %s %s %s'%(deal.user,deal.time,deal.instrument,deal.price))
            
    def sendTimeBarInfo(self,timebarinfo):
        print("send timebarinfo")
        if self.master != None:
            self.master.send('%s--%s:%s %s'%(timebarinfo.user,timebarinfo.time,timebarinfo.instrument,timebarinfo.price))

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
