# coding: utf-8

from mimiron.api import app 
from mimiron.ext import db

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()

