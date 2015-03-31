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

class ConditionGroup(Base):

    __tablename__ = 'condition_group'

    appname = db.Column(db.String(30), unique=True, nullable=False)
    operator = db.Column(db.CHAR(5), nullable=False, default='')

    conditions = db.relationship('Condition', backref='condition_group', lazy='dynamic')

    def __init__(self, appname, operator=''):
        self.appname = appname
        self.operator = operator

    @classmethod
    def create(cls, appname, operator='', **conditions):
        try:
            cg = cls(appname, operator)
            db.session.add(cg)
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
    def get_by_appname(cls, appname):
        return cls.query.filter(cls.appname == appname).all()

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
        d.update(conditions=self.conditions.all())
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
