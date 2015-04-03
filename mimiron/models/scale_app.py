# coding: utf-8

import sqlalchemy.exc

from mimiron.ext import db
from mimiron.models.base import Base
from mimiron.models.record import Record

class ScaleApp(Base):

    __tablename__ = 'scale_app'
    __table_args__ = db.UniqueConstraint('appname', 'version', 'entrypoint', 'env'),

    appname = db.Column(db.String(30), nullable=False)
    version = db.Column(db.String(50), nullable=False)
    entrypoint = db.Column(db.CHAR(20), nullable=False)
    env = db.Column(db.CHAR(20), nullable=False)

    condition_groups = db.relationship('ConditionGroup', backref='scale_app', lazy='dynamic')
    records = db.relationship('Record', backref='scale_app', lazy='dynamic')

    def __init__(self, appname, version, entrypoint, env):
        self.appname = appname
        self.version = version
        self.entrypoint = entrypoint
        self.env = env

    @classmethod
    def list_all(cls, start=0, limit=None):
        q = cls.query.offset(start)
        if limit is not None:
            q = q.limit(limit)
        return q.all()

    @classmethod
    def get_or_create(cls, appname, version, entrypoint, env):
        app = cls.query.filter_by(appname=appname, version=version,
                entrypoint=entrypoint, env=env).first()
        if app:
            return app
        try:
            app = cls(appname, version, entrypoint, env)
            db.session.add(app)
            db.session.commit()
            return app
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
            return None

    @classmethod
    def get_by_appname(cls, appname, start=0, limit=None):
        q = cls.query.filter_by(appname=appname).offset(start)
        if limit is not None:
            q = q.limit(limit)
        return q.all()

    def add_record(self, container_id):
        try:
            r = Record(container_id)
            db.session.add(r)
            self.records.append(r)
            db.session.commit()
            return r
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
            return None

    def list_records(self, start=0, limit=None):
        q = self.records.order_by(Record.id.desc()).offset(start)
        if limit is not None:
            q = q.limit(limit)
        return q.all()

    def delete(self):
        for cg in self.condition_groups.all():
            cg.delete()
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        d = super(ScaleApp, self).to_dict()
        d.update(condition_groups=self.condition_groups.all())
        return d

