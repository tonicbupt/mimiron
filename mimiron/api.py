# coding: utf-8

from flask import Flask, request

from mimiron.condition import ConditionGroup
from mimiron.utils import jsonify
from mimiron.ext import db

app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)

@app.route('/api/app/<appname>/conditions/', methods=['GET'])
@jsonify
def list_conditions(appname):
    return ConditionGroup.get_by_appname(appname)

@app.route('/api/condition_group/<cg_id>/', methods=['GET'])
@jsonify
def get_condition_group(cg_id):
    return ConditionGroup.get(cg_id)

@app.route('/api/condition_group/<cg_id>/delete/', methods=['DELETE', 'POST'])
@jsonify
def delete_condition_group(cg_id):
    cg = ConditionGroup.get(cg_id)
    if cg:
        cg.delete()
    return {'r': 0, 'msg': 'ok'}

@app.route('/api/<appname>/add_conditions/', methods=['GET', 'POST'])
@jsonify
def add_conditions(appname):
    """
    数据是这个样子:
    {
        'operator': 'and',
        'conditions': {
            'cpu': '80',
            'io': '50',
        },
    }
    """
    data = request.get_json()
    operator = data.get('operator', '')
    conditions = data.get('conditions', None)
    if conditions is None:
        return {'r': 1, 'msg': 'No conditions set'}
    if len(conditions) > 1 and not operator:
        return {'r': 1, 'msg': 'Conditions more than one, must set operator'}
    cg = ConditionGroup.create(appname, operator, **conditions)
    if not cg:
        return {'r': 1, 'msg': 'Condition Group create failed'}
    return {'r': 0, 'msg': 'ok', 'condition_group': cg}

