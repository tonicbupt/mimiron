# coding: utf-8

from mimiron.condition import ConditionGroup, ScaleApp

def test_scale_app(test_db):
    apps = ScaleApp.list_all()
    assert len(apps) == 0

    app = ScaleApp.get_or_create('app', 'version', 'entrypoint', 'env')
    assert app is not None
    app2 = ScaleApp.get_or_create('app', 'version', 'entrypoint', 'env')
    assert app2.id == app.id
    app.delete()

    apps = ScaleApp.list_all()
    assert len(apps) == 0

    app = ScaleApp.get_or_create('app', 'version', 'entrypoint', 'env1')
    app2 = ScaleApp.get_or_create('app', 'version', 'entrypoint', 'env2')
    assert app.id != app2.id
    assert app.appname == app2.appname
    assert app.version == app2.version
    assert app.entrypoint == app2.entrypoint
    assert app.env != app2.env
    assert len(app.condition_groups.all()) == len(app2.condition_groups.all()) == 0

    app.delete()
    app2.delete()

    apps = ScaleApp.list_all()
    assert len(apps) == 0

def test_condition_group(test_db):
    cg = ConditionGroup.create('app', 'version', 'entrypoint', 'env', 'cgname', cpu=80, io=50, network=70)
    cs = cg.conditions.all()

    apps = ScaleApp.list_all()
    assert len(apps) == 1
    assert apps[0].appname == 'app'
    assert apps[0].version== 'version'
    assert len(apps[0].condition_groups.all()) == 1
    assert apps[0].condition_groups.all()[0].id == cg.id

    assert len(cs) == 3
    cdict = {c.key: c.value for c in cs}
    assert cdict == {'cpu': '80', 'io': '50', 'network': '70'}

    cg.add_conditions(disk=80, memory=80)
    cs = cg.conditions.all()
    assert len(cs) == 5
    cdict = {c.key: c.value for c in cs}
    assert cdict == {'cpu': '80', 'io': '50', 'network': '70', 'disk': '80', 'memory': '80'}

    cg.delete()
    cg = ConditionGroup.get(cg.id)
    assert cg is None

def test_condition(test_db):
    cg = ConditionGroup.create('app', 'version', 'entrypoint', 'env', 'cgname', cpu=80, io=50)
    cs = cg.conditions.all()

    assert len(cs) == 2
    cdict = {c.key: c.value for c in cs}
    assert cdict == {'cpu': '80', 'io': '50'}

    cg.add_conditions(disk=80, memory=80)
    cs = cg.conditions.all()
    assert len(cs) == 4
    cdict = {c.key: c.value for c in cs}
    assert cdict == {'cpu': '80', 'io': '50', 'disk': '80', 'memory': '80'}

    for c in cs:
        if c.key in ('cpu', 'memory'):
            c.delete()
    cs = cg.conditions.all()
    assert len(cs) == 2
    cdict = {c.key: c.value for c in cs}
    assert cdict == {'io': '50', 'disk': '80'}

def test_clean(test_db):
    app = ScaleApp.get_or_create('app', 'version', 'entrypoint', 'env')
    assert len(ScaleApp.list_all()) == 1

    cg = ConditionGroup.create('app', 'version', 'entrypoint', 'env', 'cgname', cpu=80, io=50, network=70)
    assert len(ScaleApp.list_all()) == 1
    assert len(cg.conditions.all()) == 3

    app.delete()
    assert len(ScaleApp.list_all()) == 0
    assert len(cg.conditions.all()) == 0
    assert ConditionGroup.get_by_name('cgname') is None
