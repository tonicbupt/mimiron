# coding: utf-8

import json
from flask import url_for
from mimiron.condition import ConditionGroup

def test_list_conditions(client, test_db):
    rv = client.get(url_for('list_conditions', appname='app'))
    r = json.loads(rv.data)
    assert rv.status_code == 200
    assert len(r) == 0

    rv = client.get(url_for('get_condition_group', cg_id=1))
    r = json.loads(rv.data)
    assert rv.status_code == 200
    assert r is None

    cg = ConditionGroup.create('app', 'and', cpu=80, io=50)

    rv = client.get(url_for('get_condition_group', cg_id=cg.id))
    r = json.loads(rv.data)
    assert rv.status_code == 200
    assert r['appname'] == 'app'
    assert r['operator'] == 'and'
    assert len(r['conditions']) == 2

    rv = client.get(url_for('list_conditions', appname='app'))
    r = json.loads(rv.data)
    assert rv.status_code == 200
    assert len(r) == 1

    assert r[0]['appname'] == 'app'
    assert r[0]['operator'] == 'and'
    cs = r[0]['conditions']
    assert len(cs) == 2
    assert set('%s:%s' % (c['key'], c['value']) for c in cs) == {'cpu:80', 'io:50'}

def test_delete_condition_group(client, test_db):
    cg = ConditionGroup.create('app', 'and', cpu=80, io=50)

    rv = client.get(url_for('get_condition_group', cg_id=cg.id))
    r = json.loads(rv.data)
    assert rv.status_code == 200
    assert r['appname'] == 'app'
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
        'operator': 'or',
        'conditions': {
            'cpu': '60',
            'io': '50',
        },
    }
    rv = client.post(url_for('add_conditions', appname='app'),
            data=json.dumps(data), content_type='application/json')
    r = json.loads(rv.data)
    assert rv.status_code == 200
    assert r['r'] == 0
    cg = r['condition_group']
    assert len(cg['conditions']) == 2
    assert cg['operator'] == 'or'
    assert cg['appname'] == 'app'

    rv = client.get(url_for('get_condition_group', cg_id=cg['id']))
    r = json.loads(rv.data)
    assert r == cg
