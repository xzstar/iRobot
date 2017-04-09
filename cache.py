#!/Library/Frameworks/Python.framework/Versions/3.5/bin/python3
from io import StringIO


class TimeBarInfoCache:
    '''
    TimeBarInfo Cache the data for Use
    '''

    def __init__(self):
        self.timebarinfocache = {}
        self.heartbeatcache = {}

    def update_timebarinfo(self, barinfo):
        if barinfo.user in self.timebarinfocache:
            print('in Cache : %s' % (barinfo.user))
            datacache = self.timebarinfocache[barinfo.user]
            datacache[barinfo.instrument] = barinfo
        else:
            print('not in Cache : %s' % (barinfo.user))
            self.timebarinfocache[barinfo.user] = {barinfo.instrument: barinfo}

    def update_heartbeat(self, heartbeat):
        if heartbeat.user in self.heartbeatcache:
            print('heartbeat in Cache : %s' % (heartbeat.user))
        else:
            print('heartbeat not in Cache : %s' % (heartbeat.user))

        self.heartbeatcache[heartbeat.user] = heartbeat

    def __str__(self):
        rtnvalue = StringIO()
        rtnvalue.write('{\n')
        for(user, datacache) in self.timebarinfocache.items():
            rtnvalue.write('#用户=')
            rtnvalue.write(user)
            rtnvalue.write('\n')

            rtnvalue.write('#心跳=')
            if user in self.heartbeatcache:
                rtnvalue.write(str(self.heartbeatcache[user]))
            rtnvalue.write('\n')

            for barinfo in datacache.values():
                rtnvalue.write(str(barinfo))
                rtnvalue.write('\n')
        rtnvalue.write('}')
        return rtnvalue.getvalue()
