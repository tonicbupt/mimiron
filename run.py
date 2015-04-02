# coding: utf-8

from mimiron.api import app
from mimiron.scaler import Scaler

def start_api():
    app.run()

def start_scaler():
    scaler = Scaler()
    scaler.run()

if __name__ == '__main__':
    start_api()

