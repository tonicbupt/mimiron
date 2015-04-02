# coding: utf-8

import json
from flask import url_for
from mimiron.condition import ConditionGroup

def test_list_app_scales(client, test_db):
    rv = client.get(url_for('list_app_scales', appname='app'))
    r = json.loads(rv.data)
    assert rv.status_code == 200
    assert len(r) == 0

    ConditionGroup.create('app', 'version', 'entrypoint', 'env1', 'cgname1', cpu=80, io=50)
    ConditionGroup.create('app', 'version', 'entrypoint', 'env2', 'cgname2', cpu=80, io=50)

    rv = client.get(url_for('list_app_scales', appname='app'))
    r = json.loads(rv.data)
    assert rv.status_code == 200
    assert len(r) == 2
    sa1, sa2 = r

    rv = client.get(url_for('get_scale_app', scale_app_id=sa1['id']))
    r = json.loads(rv.data)
    assert rv.status_code == 200
    assert r['appname'] == 'app'
    assert r['env'] == 'env1'

    rv = client.get(url_for('get_scale_app', scale_app_id=sa2['id']))
    r = json.loads(rv.data)
    assert rv.status_code == 200
    assert r['appname'] == 'app'
    assert r['env'] == 'env2'

def test_list_scale_app_conditions(client, test_db):
    rv = client.get(url_for('get_condition_group', cg_id=1))
    r = json.loads(rv.data)
    assert rv.status_code == 200
    assert r is None

    cg = ConditionGroup.create('app', 'version', 'entrypoint', 'env', 'cgname', cpu=80, io=50)

    rv = client.get(url_for('list_scale_app_conditions', scale_app_id=cg.scale_app_id))
    r = json.loads(rv.data)
    assert rv.status_code == 200
    assert len(r) == 1
    assert r[0]['name'] == 'cgname'
    assert r[0]['scale_app_id'] == cg.scale_app_id
    cs = r[0]['conditions']
    assert len(cs) == 2
    assert set('%s:%s' % (c['key'], c['value']) for c in cs) == {'cpu:80', 'io:50'}

    rv = client.get(url_for('get_condition_group', cg_id=cg.id))
    r = json.loads(rv.data)
    assert rv.status_code == 200
    assert r['name'] == 'cgname'
    assert r['scale_app_id'] == cg.scale_app_id
    assert len(r['conditions']) == 2

def test_delete_condition_group(client, test_db):
    cg = ConditionGroup.create('app', 'version', 'entrypoint', 'env', 'cgname', cpu=80, io=50)

    rv = client.get(url_for('get_condition_group', cg_id=cg.id))
    r = json.loads(rv.data)
    assert rv.status_code == 200
    assert r['name'] == 'cgname'
    assert len(r['conditions']) == 2

    rv = client.delete(url_for('delete_condition_group', cg_id=cg.id))
    r = json.loads(rv.data)
    assert r == {'r': 0, 'msg': 'ok'}

    rv = client.get(url_for('get_condition_group', cg_id=cg.id))
    r = json.loads(rv.data)
    assert rv.status_code == 200
    assert r is None

def test_add_conditions(client, test_db):
    data = {
        'name': 'cgname',
        'entrypoint': 'entrypoint',
        'env': 'env',
        'conditions': {
            'cpu': '60',
            'io': '50',
        },
    }
    rv = client.post(url_for('add_conditions', appname='app', version='version'),
            data=json.dumps(data), content_type='application/json')
    r = json.loads(rv.data)
    assert rv.status_code == 200
    assert r['r'] == 0
    cg = r['condition_group']
    assert len(cg['conditions']) == 2
    assert cg['name'] == 'cgname'

    rv = client.get(url_for('get_condition_group', cg_id=cg['id']))
    r = json.loads(rv.data)
    assert r == cg

    rv = client.get(url_for('list_scale_app_conditions', scale_app_id=cg['scale_app_id']))
    r = json.loads(rv.data)
    assert rv.status_code == 200
    assert len(r) == 1
    assert r[0]['name'] == 'cgname'
    assert r[0]['scale_app_id'] == cg['scale_app_id']
    cs = r[0]['conditions']
    assert len(cs) == 2
    assert set('%s:%s' % (c['key'], c['value']) for c in cs) == {'cpu:60', 'io:50'}

def test_delete_scale_app(client, test_db):
    cg1 = ConditionGroup.create('app', 'version', 'entrypoint', 'env', 'cgname1', cpu=80, io=50)
    cg2 = ConditionGroup.create('app', 'version', 'entrypoint', 'env', 'cgname2', cpu=80, io=50)

    rv = client.get(url_for('get_condition_group', cg_id=cg1.id))
    r = json.loads(rv.data)
    assert rv.status_code == 200
    assert r['name'] == 'cgname1'
    assert len(r['conditions']) == 2

    rv = client.get(url_for('get_condition_group', cg_id=cg2.id))
    r = json.loads(rv.data)
    assert rv.status_code == 200
    assert r['name'] == 'cgname2'
    assert len(r['conditions']) == 2

    rv = client.delete(url_for('delete_scale_app', scale_app_id=cg1.id))
    r = json.loads(rv.data)
    assert r == {'r': 0, 'msg': 'ok'}

    rv = client.get(url_for('get_condition_group', cg_id=cg1.id))
    r = json.loads(rv.data)
    assert rv.status_code == 200
    assert r is None

    rv = client.get(url_for('get_condition_group', cg_id=cg2.id))
    r = json.loads(rv.data)
    assert rv.status_code == 200
    assert r is None

    rv = client.get(url_for('list_app_scales', appname='app'))
    r = json.loads(rv.data)
    assert rv.status_code == 200
    assert len(r) == 0

    rv = client.get(url_for('get_scale_app', scale_app_id=cg1.scale_app_id))
    r = json.loads(rv.data)
    assert rv.status_code == 200
    assert r is None

