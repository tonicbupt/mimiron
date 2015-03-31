# coding: utf-8

import json
from datetime import datetime
from functools import wraps
from flask import Response

from mimiron.condition import Base

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

