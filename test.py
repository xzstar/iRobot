#!/Library/Frameworks/Python.framework/Versions/3.5/bin/python3
'''
Test code for iRobot
'''
import time
import redis
CHANNELS = ('deal', 'timebarinfo', 'heartbeat')

REDIS_CONN = redis.StrictRedis()

REDIS_CONN.publish(CHANNELS[0],
                   '{"user":"xiezhe",\
        "instrument":"rb1710",\
        "direction":"1",\
        "holders":"2",\
        "price":"1000",\
        "time":"2017-1-1"}')
REDIS_CONN.publish(CHANNELS[1],
                   '{"user":"xiezhe",\
    "instrument":"rb1710",\
    "price":"1000",\
    "time":"2017-1-1"}')
TS = int(time.time())
TS_STRING = '{"user":"xiezhe","timestamp":%d}' % TS
REDIS_CONN.publish(CHANNELS[2], TS_STRING)

REDIS_CONN.publish(CHANNELS[1],
                   '{"user":"xiezhe",\
    "instrument":"rb1710",\
    "price":"1002",\
    "time":"2017-1-1"}')

REDIS_CONN.publish(CHANNELS[1],
                   '{"user":"xiezhe",\
    "instrument":"rm1709",\
    "price":"1002",\
    "time":"2017-1-1"}')
