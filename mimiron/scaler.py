# coding: utf-8

import sys
import signal
import time
from influxdb import InfluxDBClient

from mimiron.condition import ConditionGroup
from config import (INFLUXDB_HOST, INFLUXDB_PORT, INFLUXDB_USER,
        INFLUXDB_PASSWORD, INFLUXDB_DATABASE)

client = InfluxDBClient(INFLUXDB_HOST, INFLUXDB_PORT, INFLUXDB_USER,
        INFLUXDB_PASSWORD, INFLUXDB_DATABASE)

def _test_condition_group(condition_groups):
    """所有的条件组的关系是or, 有一个满足即进行扩容.
    单个条件组里的所有条件的关系是and, 必须全部满足
    """
    for cg in condition_groups:
        if all(_test_condition(cg.appname, c.key, c.value) for c in cg.conditions.all()):
            return True
    return False

# TODO version env 都需要
def _test_condition(appname, entrypoint, indicator, value):
    """测试指标是不是已经超过.
    很简单, 每1min的数据采集, 如果前10分钟的平均值超过了value, 就认为超过
    """
    sql = ("select derivative(value) from %s "
           "where metric='%s' and entrypoint='%s' "
           "group by time(1m) limit 10" % (appname, indicator. entrypoint))
    r = client.query(sql)
    if not r:
        return False
    r = r[0]
    avg = sum([p[1] for p in r['points']]) / len(r['points'])
    return avg > float(value)
    
class Scaler(object):

    def __init__(self):
        self.conditions = []
        self.load_apps()
        signal.signal(signal.SIGHUP, self.handle_sighup)
        signal.signal(signal.SIGKILL, self.handle_sigkill)

    def handle_sighup(self, s, f):
        print 'SIGHUP got, reload'
        self.load_apps()

    def handle_sigkill(self, s, f):
        print 'SIGKILL got, exit'
        sys.exit(0)

    def load_apps(self):
        self.conditions = ConditionGroup.list_all()
    
    def scan_single_app(cg):
        if _test_condition_group(cgs):
            # do scale
            pass
    
    def run(self):
        while True:
            for app in self.apps:
                self.scan_single_app(app)
                time.sleep(60)
