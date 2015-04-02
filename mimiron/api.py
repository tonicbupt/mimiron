# coding: utf-8

from flask import Flask, request

from mimiron.condition import ConditionGroup, ScaleApp
from mimiron.utils import jsonify
from mimiron.ext import db

app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)

@app.route('/api/app/<appname>/scales/', methods=['GET'])
@jsonify
def list_app_scales(appname):
    return ScaleApp.get_by_appname(appname)

@app.route('/api/scale_app/<scale_app_id>/', methods=['GET'])
@jsonify
def get_scale_app(scale_app_id):
    return ScaleApp.get(scale_app_id)

@app.route('/api/scale_app/<scale_app_id>/conditions/', methods=['GET'])
@jsonify
def list_scale_app_conditions(scale_app_id):
    app = ScaleApp.get(scale_app_id)
    return app.condition_groups.all()

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

@app.route('/api/scale_app/<scale_app_id>/delete/', methods=['DELETE', 'POST'])
@jsonify
def delete_scale_app(scale_app_id):
    app = ScaleApp.get(scale_app_id)
    if app:
        app.delete()
    return {'r': 0, 'msg': 'ok'}

@app.route('/api/<appname>/<version>/add_conditions/', methods=['GET', 'POST'])
@jsonify
def add_conditions(appname, version):
    """
    数据是这个样子:
    {
        'env': 'env',
        'name': 'cgname',
        'entrypoint': 'entrypoint',
        'conditions': {
            'cpu': '80',
            'io': '50',
        },
    }
    """
    data = request.get_json()
    conditions = data.get('conditions', None)
    if conditions is None:
        return {'r': 1, 'msg': 'No conditions set'}
    if not 'name' in data or not 'entrypoint' in data or not 'env' in data:
        return {'r': 1, 'msg': 'No cgname/entrypoint/env set'}
    cg = ConditionGroup.create(appname, version, data['entrypoint'],
            data['env'], data['name'], **conditions)
    if not cg:
        return {'r': 1, 'msg': 'Condition Group create failed'}
    return {'r': 0, 'msg': 'ok', 'condition_group': cg}

