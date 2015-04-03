# coding: utf-8

import sqlalchemy.exc

from mimiron.ext import db
from mimiron.models.base import Base
from mimiron.models.scale_app import ScaleApp

__all__ = ['ConditionGroup', 'Condition']

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

