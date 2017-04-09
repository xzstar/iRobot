#!/usr/bin/env python


class FackWeiXinClient:

    def __init__(self, tag):
        self.heartbeat_dict = {}
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def sendDeal(self, deal):
        print("send Deal")

    def sendTimeBarInfo(self, timebarinfo):
        print("send timebarinfo")
        print('均值 %s--%s:%s %s' %
              (timebarinfo.user, timebarinfo.time, timebarinfo.instrument, timebarinfo.price))

    def sendHeartBeat(self, heartbeat):
        print("send heartbeat")

    def sendWarnHeartBeat(self, heartbeat, OK):
        print("send warn heartbeat")
        if OK:
            msg = "OK"
        else:
            msg = "Error"
        print('%s-- last heartbeat %s %s' %
              (heartbeat.user, heartbeat.timestamp, msg))
