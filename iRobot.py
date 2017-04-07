#!/usr/bin/env python
import redis
import json
import threading
import time
from weixinclient import WeiXinClient

Lock = threading.Lock()
        

class Deal:
    def __init__(self,user,instrument,direction,holders,price,time):
        self.user = user
        self.instrument = instrument
        self.direction = direction
        self.holders = holders
        self.price = price
        self.time = time

class DealDecoder(json.JSONDecoder):
    def decode(self,s):
        dic = super().decode(s)
        return Deal(dic['user'],dic['instrument'],dic['direction'],
        dic['holders'],dic['price'],dic['time'])

class TimeBarInfo:
    def __init__(self,user,instrument,price,time):
        self.user = user
        self.instrument = instrument
        self.price = price
        self.time = time

class TimebarInfoDecoder(json.JSONDecoder):
    def decode(self,s):
        dic = super().decode(s)
        return TimeBarInfo(dic['user'],dic['instrument'],
        dic['price'],dic['time'])


class HeartBeat:
    def __init__(self,user,timestamp):
        self.user = user
        self.timestamp = timestamp

class HeartBeatDecoder(json.JSONDecoder):
    def decode(self,s):
        dic = super().decode(s)
        return HeartBeat(dic['user'],dic['timestamp'])

class Singleton(object):
    
    # 定义静态变量实例
    __instance = None

    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            try:
                Lock.acquire()
                # double check
                if not cls.__instance:
                    cls.__instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
            finally:
                Lock.release()
        return cls.__instance

class HeartBeatWorkerThread(threading.Thread):
    def __init__(self,sleep_time):
        super(HeartBeatWorkerThread, self).__init__()
        if sleep_time < 30:
            self.sleep_time = sleep_time
        else:
            self.sleep_time = 30        
        self._running = False
        self._triggerstop = False
        self._hasWarn = {}

    def run(self):
        if self._running:
            return
        self._running = True
        sleep_time = self.sleep_time
        time.sleep(self.sleep_time)
        while self._triggerstop == False:
            current = int(time.time())
            print("WorkThread:%d" % (current))
            for key in wxClient.heartbeat_dict:
                timeValue = wxClient.heartbeat_dict[key]
                diff = current - timeValue;
                
                if key in self._hasWarn:
                    if diff < 60 :
                        del self._hasWarn[key]
                        heartbeat = HeartBeat(key,timeValue)
                        wxClient.sendWarnHeartBeat(heartbeat,True)
                        print("WorkThread: reset %s" % (key))
                else:
                    if diff > 60:
                        self._hasWarn[key] = timeValue
                        heartbeat = HeartBeat(key,timeValue)
                        wxClient.sendWarnHeartBeat(heartbeat,False)
                        print("WorkThread: warn %s" % (key))

            time.sleep(self.sleep_time)      
                    
        self._running = False

    def stopRunning(self):
        if self._running == True:
            self._triggerstop = True
        
    def stop(self):
        # stopping simply unsubscribes from all channels and patterns.
        # the unsubscribe responses that are generated will short circuit
        # the loop in run(), calling pubsub.close() to clean up the connection
        #self.pubsub.unsubscribe()
        #self.pubsub.punsubscribe()
        pass

class Handler:
    @staticmethod
    def handle_deal(message):
        data = str(message['data'],'utf-8')
        print(data)
        deal = json.loads(data,cls=DealDecoder)
        print(deal.user)
        print(deal.instrument)
        print(deal.direction)
        print(deal.holders)
        print(deal.price)
        wxClient.sendDeal(deal)

    @staticmethod
    def handle_timebarinfo(message):
        data = str(message['data'],'utf-8')
        timebarinfo = json.loads(data,cls=TimebarInfoDecoder)
        print('TimebarInfo:%s %s' % (timebarinfo.user,timebarinfo.time))
        wxClient.sendTimeBarInfo(timebarinfo)

    @staticmethod
    def handle_heartbeat(message):
        data = str(message['data'],'utf-8')
        heartbeat = json.loads(data,cls=HeartBeatDecoder)
        print('HeartBeat:%s %s' % (heartbeat.user,heartbeat.timestamp))
        wxClient.sendHeartBeat(heartbeat)

wxClient = WeiXinClient("star")
wxClient.start()

redisconn = redis.StrictRedis()
redispublish = redisconn.pubsub()

redispublish.subscribe(**{'deal':Handler.handle_deal})
redispublish.subscribe(**{'timebarinfo':Handler.handle_timebarinfo})
redispublish.subscribe(**{'heartbeat':Handler.handle_heartbeat})

thread_handle_deal = redispublish.run_in_thread(sleep_time=5)
thread_heartbeat = HeartBeatWorkerThread(sleep_time = 30)

thread_heartbeat.start()
while True:
    info = input("command:")  
    if info == 'stop':  
        print ('停止')  
        thread_handle_deal.stop()
        wxClient.stop()
        thread_heartbeat.stopRunning()
        break;  

