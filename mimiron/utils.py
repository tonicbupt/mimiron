# coding: utf-8

import json
from flask import Response
from datetime import datetime
from functools import wraps

from mimiron.models.base import Base

class EruJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Base):
            return obj.to_dict()
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super(EruJSONEncoder, self).default(obj)

def jsonify(f):
    @wraps(f)
    def _(*args, **kwargs):
        r = f(*args, **kwargs)
        return Response(json.dumps(r, cls=EruJSONEncoder), mimetype='application/json')
    return _

def json_failed(r):
    return 'r' in r and r['r'] == 1

