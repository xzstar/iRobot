#!/usr/bin/env python
import datetime
from wxpy import *


class WeiXinClient:

    def __init__(self, tag, cache):
        self.bot = None
        self.master = None
        self.tag = tag
        self.cache = cache

    def start(self):
        self.bot = Bot(cache_path=True)
        self.master = self.bot.groups().search('机器人')[0]

        @self.bot.register(Group, TEXT)
        def handle_msg(message):
            if message.text == '均值' or message.text == 'avg':
                self.master.send(str(self.cache))

    def stop(self):
        pass
        # if self.bot != None:
        #    self.bot.logout()

    def sendDeal(self, deal):
        print("send Deal")
        if self.master != None:
            self.master.send('成交 %s %s %s %s %s'
                             % (deal.user, deal.time, deal.instrument, deal.price, deal.holders))

    def sendTimeBarInfo(self, timebarinfo):
        print("send timebarinfo")
        if self.master != None:
            self.master.send('均值 %s--%s:%s %s'
                             % (timebarinfo.user, timebarinfo.time, timebarinfo.instrument, timebarinfo.price))

    def sendHeartBeat(self, heartbeat):
        pass

    def sendWarnHeartBeat(self, heartbeat, OK):
        print("send warn heartbeat")
        if OK:
            msg = "OK"
        else:
            msg = "Error"
        if self.master != None:
            self.master.send('%s-- last heartbeat %s %s'
                             % (heartbeat.user, datetime.datetime.fromtimestamp(heartbeat.timestamp), msg))
