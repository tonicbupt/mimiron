# coding: utf-8

import sqlalchemy.exc
from sqlalchemy.ext.declarative import declared_attr
from mimiron.ext import db

__all__ = ['ConditionGroup', 'Condition']

class Base(db.Model):

    __abstract__ = True

    @declared_attr
    def id(cls):
        return db.Column('id', db.Integer, primary_key=True, autoincrement=True)

    @classmethod
    def get(cls, id):
        return cls.query.filter(cls.id==id).first()

    @classmethod
    def get_multi(cls, ids):
        return [cls.get(i) for i in ids]

    def to_dict(self):
        keys = [c.key for c in self.__table__.columns]
        return {k: getattr(self, k) for k in keys}

    def __repr__(self):
        attrs = ', '.join('{0}={1}'.format(k, v) for k, v in self.to_dict().iteritems())
        return '{0}({1})'.format(self.__class__.__name__, attrs)

class ScaleApp(Base):

    __tablename__ = 'scale_app'
    __table_args__ = db.UniqueConstraint('appname', 'version', 'entrypoint', 'env'),

    appname = db.Column(db.String(30), nullable=False)
    version = db.Column(db.String(50), nullable=False)
    entrypoint = db.Column(db.CHAR(20), nullable=False)
    env = db.Column(db.CHAR(20), nullable=False)

    condition_groups = db.relationship('ConditionGroup', backref='scale_app', lazy='dynamic')

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

    def delete(self):
        for cg in self.condition_groups.all():
            cg.delete()
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        d = super(ScaleApp, self).to_dict()
        d.update(condition_groups=self.condition_groups.all())
        return d

class ConditionGroup(Base):

    __tablename__ = 'condition_group'

    name = db.Column(db.String(30), index=True, nullable=False, default='')

    conditions = db.relationship('Condition', backref='condition_group', lazy='dynamic')
    scale_app_id = db.Column(db.Integer, db.ForeignKey('scale_app.id'))

    def __init__(self, name):
        self.name = name

    @classmethod
    def create(cls, appname, version, entrypoint, env, cgname, **conditions):
        app = ScaleApp.get_or_create(appname, version, entrypoint, env)
        try:
            cg = cls(cgname)
            db.session.add(cg)
            app.condition_groups.append(cg)
            if conditions:
                for key, value in conditions.iteritems():
                    condition = Condition(key, value)
                    db.session.add(condition)
                    cg.conditions.append(condition)
            db.session.commit()
            return cg
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
            return None

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter(cls.name==name).first()

    def add_conditions(self, **kw):
        for key, value in kw.iteritems():
            condition = Condition(key, value)
            db.session.add(condition)
            self.conditions.append(condition)
        db.session.add(self)
        db.session.commit()
        return True

    def delete(self):
        for con in self.conditions.all():
            con.delete()
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        d = super(ConditionGroup, self).to_dict()
        d.update(conditions=self.conditions.all(), scale_app_id=self.scale_app_id)
        return d

class Condition(Base):

    __tablename__ = 'condition'

    key = db.Column(db.String(30), nullable=False)
    value = db.Column(db.String(30), nullable=False)
    condition_group_id = db.Column(db.Integer, db.ForeignKey('condition_group.id'))

    def __init__(self, key, value):
        self.key = key
        self.value = value

    @classmethod
    def create(cls, key, value):
        try:
            c = cls(key, value)
            db.session.add(c)
            db.session.commit()
            return c
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
            return None

    def edit(self, value):
        self.value = value
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

