# coding: utf-8

import sys
import signal
import time
from influxdb import InfluxDBClient

from mimiron.client import EruClient
from mimiron.models.condition import ScaleApp
from mimiron.utils import json_failed
from config import (
    INFLUXDB_HOST,
    INFLUXDB_PORT,
    INFLUXDB_USER,
    INFLUXDB_PASSWORD,
    INFLUXDB_DATABASE,
    ERU_URL,
    ERU_TIMEOUT,
    ERU_USER,
    ERU_PASSWORD,
)

influxdb_client = InfluxDBClient(INFLUXDB_HOST, INFLUXDB_PORT, INFLUXDB_USER,
        INFLUXDB_PASSWORD, INFLUXDB_DATABASE)
eru_client = EruClient(ERU_URL, ERU_TIMEOUT, ERU_USER, ERU_PASSWORD)


def _test_scale_app(scale_app):
    """所有的条件组的关系是or, 有一个满足即进行扩容.
    单个条件组里的所有条件的关系是and, 必须全部满足
    """
    for cg in scale_app.condition_groups.all():
        if all(_test_condition(scale_app.appname,
            scale_app.entrypoint, c.key, c.value) for c in cg.conditions.all()):
            return True
    return False

# TODO version env 都需要
def _test_condition(appname, entrypoint, indicator, value):
    """测试指标是不是已经超过.
    很简单, 每1min的数据采集, 如果前10分钟的平均值超过了value, 就认为超过
    """
    sql = ("select derivative(value) from %s "
           "where metric='%s' and entrypoint='%s' "
           "group by time(1m) limit 10" % (appname, indicator, entrypoint))
    r = influxdb_client.query(sql)
    if not r:
        return False
    r = r[0]
    avg = sum([p[1] for p in r['points']]) / len(r['points'])
    return avg > float(value)

def do_scale(scale_app):
    info = eru_client.get_scale_info(scale_app.appname, scale_app.version)
    if json_failed(info):
        return
    eru_client.deploy_private(info['group'], info['pod'], scale_app.appname,
            info['ncore'], 1, scale_app.version, scale_app.entrypoint, scale_app.env)
    
class Scaler(object):

    def __init__(self):
        self.scale_apps = []
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
        self.scale_apps = ScaleApp.list_all()
    
    def scan_scale_app(self, scale_app):
        if _test_scale_app(scale_app):
            do_scale(scale_app)
    
    def run(self):
        while True:
            for scale_app in self.scale_apps:
                self.scan_scale_app(scale_app)
                time.sleep(60)
