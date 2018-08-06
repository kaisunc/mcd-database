# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 11:42:37 2017

@author: julio
"""

pg_db_username = 'postgres'
pg_db_password = ''
pg_db_name = 'mcd_database'
pg_db_hostname = '192.168.161.18'
SECRET_KEY = 'RM=#8z2aX^QKXJg'

db_string = "postgresql://{DB_USER}:{DB_PASS}@{DB_ADDR}/{DB_NAME}".format(DB_USER=pg_db_username, DB_PASS=pg_db_password, DB_ADDR=pg_db_hostname, DB_NAME=pg_db_name)

from flask import Flask
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
import json, os, datetime
import flask_whooshalchemy

#from whoosh.analysis import *
from whoosh.index import open_dir, create_in
from whoosh.fields import Schema, TEXT, ID
from whoosh import analysis


os.rmdir("/mnt/assets/whoosh_index")

app = Flask(__name__)
#app.config['WHOOSH_BASE'] = "//art-server/database/mcd_db/whoosh_index"
app.config['WHOOSH_BASE'] = "/mnt/assets/whoosh_index"
app.config['WHOOSH_ANALYZER'] = analyzer
app.config['SQLALCHEMY_DATABASE_URI'] = db_string

db = SQLAlchemy(app)

class Datatable():
    def as_dict(self):
        t = {c.name: getattr(self, c.name) for c in self.__table__.columns}    
        t["select-checkbox"] = ""
        return t

    def as_dict1(self, fields):
        selections = []
        for f in fields:
            if f['type'] == 'select':
                selections.append(f)        

        cols = {}
        for col in self.__table__.columns:
            cols[col.name] = getattr(self, col.name)
            for select in selections:
                if col.name == select['name']:
                    for opt in select['options']:
                        if getattr(self, col.name) == opt['value']:
                            cols[col.name] = opt

        cols["select-checkbox"] = ""
        return cols

class User(UserMixin, db.Model, Datatable):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)


    @property
    def password(self):
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class Logs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.Text())
    timestamp = db.Column(db.DateTime(), server_default=db.func.now(), server_onupdate=db.func.now())
    assigned = db.Column(db.Integer, db.ForeignKey('user.id'))




class Media(db.Model, Datatable):
    __tablename__ = 'media'
    __searchable__ = ['name', 'tags']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    category = db.Column(db.Integer, db.ForeignKey('category.id'))
    timestamp = db.Column(db.DateTime(), server_default=db.func.now(), server_onupdate=db.func.now())
    assigned = db.Column(db.Integer, db.ForeignKey('user.id'))
    tags = db.Column(db.Text())
    description = db.Column(db.Text())
    thumbnail = db.Column(db.Text())


class Category(db.Model, Datatable):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())    
    name_chn = db.Column(db.Text())

#%%
    
def log(message):
    logtime = datetime.datetime.utcnow()
    logdiff = logtime - program_start
    print("{0} (+{1:.3f}): {2}".format(logtime.strftime("%Y-%m-%d %H:%M:%S"),
                                    logdiff.total_seconds(),
                                    message))
                                    
def rebuild_index(model):
    model = Media
    """Rebuild search index of Flask-SQLAlchemy model"""
    
    log("Rebuilding {0} index...".format(model.__name__))
    primary_field = model.pure_whoosh.primary_key_name

    searchables = model.__searchable__
    #analyzer = model.__analyzer__
    #schema = Schema(id=ID, name=TEXT, tags=TEXT(stored=True, analyzer=analysis.StandardAnalyzer(stoplist=None, minsize=1)))
    ix = flask_whooshalchemy.whoosh_index(app, model)
    Schema(id=ID, name=TEXT, tags=TEXT(stored=True, analyzer=analysis.StandardAnalyzer(stoplist=None, minsize=1)))
    dir(ix.schema)
    ix.schema.clean()
    ix.schema.items()
    # Fetch all data
    entries = model.query.all()
    entry_count = 0
    with ix.writer() as writer:
        for entry in entries:
            index_attrs = {}
            for field in searchables:
                index_attrs[field] = unicode(getattr(entry, field))

            index_attrs[primary_field] = unicode(getattr(entry, primary_field))
            print index_attrs
            writer.update_document(**index_attrs)
            entry_count += 1

    log("Rebuilt {0} {1} search index entries.".format(str(entry_count), model.__name__))

#%%
index_writer = flask_whooshalchemy.whoosh_index(app, Media)                               
program_start = datetime.datetime.utcnow()
rebuild_index(Media)    

#%% Read the index
'''
from whoosh.index import open_dir, create_in
from whoosh.fields import Schema, TEXT, ID
from whoosh import analysis
import os
index = '//art-server/database/mcd_db/whoosh_index/Media'
if not os.path.exists(index):
    os.makedirs(index)

schema = Schema(id=ID, name=TEXT, tags=TEXT(stored=True, analyzer=analysis.StandardAnalyzer(stoplist=None, minsize=1)))
ix = create_in(index, schema)    
'''
