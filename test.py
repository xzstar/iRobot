#!/Library/Frameworks/Python.framework/Versions/3.5/bin/python3
import redis
import time
channels = ['deal','timebarinfo','heartbeat']

redisconn = redis.StrictRedis()
redisconn.publish(channels[0],'{"user":"xiezhe","instrument":"rb1710","direction":"1","holders":"2","price":"1000","time":"2017-1-1"}')
redisconn.publish(channels[1],'{"user":"xiezhe","instrument":"rb1710","price":"1000","time":"2017-1-1"}')
timestamp = int(time.time())
redisconn.publish(channels[2],'{"user":"xiezhe","timestamp":timestamp}')