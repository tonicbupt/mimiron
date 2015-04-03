# coding: utf-8

import datetime

from mimiron.ext import db
from mimiron.models.base import Base

class Record(Base):

    __tablename__ = 'record'

    time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    container_id = db.Column(db.CHAR(50), nullable=False, default='')

    scale_app_id = db.Column(db.Integer, db.ForeignKey('scale_app.id'))

    def __init__(self, container_id):
        self.container_id = container_id

    def delete(self):
        db.session.delete(self)
        db.session.commit()

