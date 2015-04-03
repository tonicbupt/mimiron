# coding: utf-8

import argparse
from mimiron.api import app
from mimiron.scaler import Scaler

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='role', help='role, must be api/scaler')
    return parser.parse_args()

def start_api():
    app.run()

def start_scaler():
    with app.app_context():
        scaler = Scaler()
        scaler.run()

if __name__ == '__main__':
    p = parse()
    if p.role == 'api':
        start_api()
    elif p.role == 'scaler':
        start_scaler()
    else:
        print 'role must be in api/scaler'

