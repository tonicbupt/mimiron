# coding: utf-8

import sys
import signal
import time
from eruhttp import EruClient
from redis import Redis

from mimiron.models.condition import ScaleApp
from mimiron.utils import json_failed
from mimiron.mock import mock_test_condition
from config import (
    ERU_URL,
    ERU_TIMEOUT,
    ERU_USER,
    ERU_PASSWORD,
    REDIS_HOST,
    REDIS_PORT,
    SCAN_INTERVAL,
    USE_MOCK,
)

eru = EruClient(ERU_URL, ERU_TIMEOUT, ERU_USER, ERU_PASSWORD)
rds = Redis(host=REDIS_HOST, port=REDIS_PORT)


def _test_scale_app(scale_app):
    """所有的条件组的关系是or, 有一个满足即进行扩容.
    单个条件组里的所有条件的关系是and, 必须全部满足
    """
    for cg in scale_app.condition_groups.all():
        if all(_test_condition(scale_app.appname,
            scale_app.entrypoint, c.key, c.value) for c in cg.conditions.all()):
            return True
    return False


def _test_condition(appname, entrypoint, indicator, value):
    """测试指标是不是已经超过.
    很简单, 每1min的数据采集, 如果前10分钟的平均值超过了value, 就认为超过
    """
    # 如果设置了 use mock, 那么就直接搞个假的
    # 因为现在的 influxdb 没有办法读数据-_-#
    if USE_MOCK:
        return mock_test_condition()


def do_scale(scale_app):
    info = eru.get_scale_info(scale_app.appname, scale_app.version)
    if json_failed(info):
        return
    dr = eru.deploy_private(info['group'], info['pod'], scale_app.appname,
            info['ncore'], 1, scale_app.version, scale_app.entrypoint, scale_app.env)
    if json_failed(dr):
        return
    # TODO 嫑阻塞主线程
    try:
        watch_key = dr['watch_keys'][0]
        task_id = dr['tasks'][0]
        pub = rds.pubsub()
        pub.subscribe(watch_key)
        for line in pub.listen():
            if line['type'] != 'message':
                continue
            if line['data'] == 'SUCCESS':
                task = eru.get_task(task_id)
                scale_app.add_record(task['props']['container_ids'][0])
                break
            else:
                break
    except:
        print 'scale failed'
    finally:
        pub.unsubscribe()
    
class Scaler(object):

    def __init__(self):
        #self.scale_apps = []
        #self.load_apps()
        #signal.signal(signal.SIGHUP, self.handle_sighup)
        signal.signal(signal.SIGTERM, self.handle_sigterm)

    def handle_sighup(self, s, f):
        print 'SIGHUP got, reload'
        self.load_apps()

    def handle_sigterm(self, s, f):
        print 'SIGTERM got, exit'
        sys.exit(0)

    def load_apps(self):
        self.scale_apps = ScaleApp.list_all()
    
    def scan_scale_app(self, scale_app):
        if _test_scale_app(scale_app):
            do_scale(scale_app)
    
    def run(self):
        try:
            while True:
                #for scale_app in self.scale_apps:
                for scale_app in ScaleApp.list_all():
                    self.scan_scale_app(scale_app)
                time.sleep(SCAN_INTERVAL)
                print >> sys.stderr, 'scanning...'
        except KeyboardInterrupt:
            print 'KeyboardInterrupt got'
            sys.exit(0)
