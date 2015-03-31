# coding: utf-8

from mimiron.condition import ConditionGroup

def test_condition_group(test_db):
    cg = ConditionGroup.create('app', 'and', cpu=80, io=50, network=70)
    cs = cg.conditions.all()

    assert len(cs) == 3
    cdict = {c.key: c.value for c in cs}
    assert cdict == {'cpu': '80', 'io': '50', 'network': '70'}
    assert cg.operator == 'and'

    cg.add_conditions(disk=80, memory=80)
    cs = cg.conditions.all()
    assert len(cs) == 5
    cdict = {c.key: c.value for c in cs}
    assert cdict == {'cpu': '80', 'io': '50', 'network': '70', 'disk': '80', 'memory': '80'}

    cg.delete()
    cg = ConditionGroup.get(cg.id)
    assert cg is None

def test_condition(test_db):
    cg = ConditionGroup.create('app', 'or', cpu=80, io=50)
    cs = cg.conditions.all()

    assert len(cs) == 2
    cdict = {c.key: c.value for c in cs}
    assert cdict == {'cpu': '80', 'io': '50'}
    assert cg.operator == 'or'

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

