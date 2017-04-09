#!/Library/Frameworks/Python.framework/Versions/3.5/bin/python3
import json
import threading
import time
import datetime
from cache import TimeBarInfoCache


import redis
from weixinclient import WeiXinClient
from fakeclient import FackWeiXinClient

LOCK = threading.Lock()


class Deal:
    '''
    Deal class
    '''

    def __init__(self, user, instrument, direction, holders, price, time):
        self.user = user
        self.instrument = instrument
        self.direction = direction
        self.holders = holders
        self.price = price
        self.time = time


class DealDecoder(json.JSONDecoder):
    '''
    Deal Decoder class
    '''

    def decode(self, s):
        dic = super().decode(s)
        return Deal(dic['user'], dic['instrument'], dic['direction'],
                    dic['holders'], dic['price'], dic['time'])


class TimeBarInfo:
    '''
    TimeBarInfo class
    '''

    def __init__(self, user, instrument, price, timebar):
        self.user = user
        self.instrument = instrument
        self.price = price
        self.time = timebar

    def __str__(self):
        return '[time=%s instrument=%s price=%s]' % (self.time, self.instrument, self.price)


class TimeBarInfoDecoder(json.JSONDecoder):
    '''
    TimeBarInfo Decoder
    '''

    def decode(self, s):
        dic = super().decode(s)
        return TimeBarInfo(dic['user'], dic['instrument'],
                           dic['price'], dic['time'])


class HeartBeat:
    '''
    HeartBeat class
    '''

    def __init__(self, user, timestamp):
        self.user = user
        self.timestamp = timestamp

    def __str__(self):
        return '[time=%s]' % datetime.datetime.fromtimestamp(self.timestamp)


class HeartBeatDecoder(json.JSONDecoder):
    '''
    HeartBeat Decoder
    '''

    def decode(self, s):
        dic = super().decode(s)
        return HeartBeat(dic['user'], dic['timestamp'])


class Singleton(object):

    # 定义静态变量实例
    __instance = None

    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            try:
                LOCK.acquire()
                # double check
                if not cls.__instance:
                    cls.__instance = super(Singleton, cls).__new__(
                        cls, *args, **kwargs)
            finally:
                LOCK.release()
        return cls.__instance


class HeartBeatWorkerThread(threading.Thread):
    '''
    HeartBeatWorkerThread
    '''

    def __init__(self, sleep_time):
        super(HeartBeatWorkerThread, self).__init__()
        if sleep_time < 30:
            self.sleep_time = sleep_time
        else:
            self.sleep_time = 30
        self._running = False
        self._triggerstop = False
        self._hasWarn = dict()

    def run(self):
        if self._running:
            return
        self._running = True
        time.sleep(self.sleep_time)
        while self._triggerstop is False:
            current = int(time.time())
            print("WorkThread:%s" % datetime.datetime.fromtimestamp(current))
            for key in timeBarInfoCache.heartbeatcache:
                timeValue = timeBarInfoCache.heartbeatcache[key].timestamp
                diff = current - timeValue

                if key in self._hasWarn:
                    if diff < 60:
                        del self._hasWarn[key]
                        heartbeat = HeartBeat(key, timeValue)
                        wxClient.sendWarnHeartBeat(heartbeat, True)
                        print("WorkThread: reset %s" % (key))
                else:
                    if diff > 60:
                        self._hasWarn[key] = timeValue
                        heartbeat = HeartBeat(key, timeValue)
                        wxClient.sendWarnHeartBeat(heartbeat, False)
                        print("WorkThread: warn %s" % (key))

            time.sleep(self.sleep_time)

        self._running = False

    def stop(self):
        # stopping simply unsubscribes from all channels and patterns.
        # the unsubscribe responses that are generated will short circuit
        # the loop in run(), calling pubsub.close() to clean up the connection
        # self.pubsub.unsubscribe()
        # self.pubsub.punsubscribe()
        if self._running is True:
            self._triggerstop = True


class Handler:
    @staticmethod
    def handle_deal(message):
        data = str(message['data'], 'utf-8')
        print(data)
        deal = json.loads(data, cls=DealDecoder)
        print(deal.user)
        print(deal.instrument)
        print(deal.direction)
        print(deal.holders)
        print(deal.price)
        wxClient.sendDeal(deal)

    @staticmethod
    def handle_timebarinfo(message):
        data = str(message['data'], 'utf-8')
        timebarinfo = json.loads(data, cls=TimeBarInfoDecoder)
        print('TimeBarInfo:%s %s' % (timebarinfo.user, timebarinfo.time))
        timeBarInfoCache.update_timebarinfo(timebarinfo)
        print(str(timeBarInfoCache))
        # wxClient.sendTimeBarInfo(timebarinfo)

    @staticmethod
    def handle_heartbeat(message):
        data = str(message['data'], 'utf-8')
        heartbeat = json.loads(data, cls=HeartBeatDecoder)
        print('HeartBeat:%s %s' % (heartbeat.user,
                                   datetime.datetime.fromtimestamp(heartbeat.timestamp)))
        timeBarInfoCache.update_heartbeat(heartbeat)
        wxClient.sendHeartBeat(heartbeat)


timeBarInfoCache = TimeBarInfoCache()

wxClient = WeiXinClient("star", timeBarInfoCache)
wxClient.start()

redisconn = redis.StrictRedis()
redispublish = redisconn.pubsub()

redispublish.subscribe(**{'deal': Handler.handle_deal})
redispublish.subscribe(**{'timebarinfo': Handler.handle_timebarinfo})
redispublish.subscribe(**{'heartbeat': Handler.handle_heartbeat})

thread_handle_deal = redispublish.run_in_thread(sleep_time=5)
thread_heartbeat = HeartBeatWorkerThread(sleep_time=30)

thread_heartbeat.start()
while True:
    INPUT_INFO = input("command:")
    if INPUT_INFO == 'stop':
        print('停止')
        thread_handle_deal.stop()
        wxClient.stop()
        thread_heartbeat.stop()
        break
