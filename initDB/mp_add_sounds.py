# -*- coding: utf-8 -*-
"""
Created on Wed Jun 27 17:13:14 2018

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
import json
import flask_whooshalchemy
import os, shutil
import multiprocessing
from whoosh.analysis import *

app = Flask(__name__)
app.config['WHOOSH_BASE'] = "//mcd-one/database/mcd_db/whoosh_index"
#app.config['WHOOSH_ANALYZER'] = analyzer
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

#%%
sound_path = u"d:/Hybrid Library"
dirs = os.listdir(sound_path)
this_tag = dirs[4]
this_path = "%s/%s" % (sound_path, this_tag)
#%%
def addFile(q):
    global sound_path
    global this_tag
    global this_path
    while q.qsize() != 0:
        name, root = q.get(block=True)
        tags = root.replace(sound_path,"")[1:].split("\\")
        tags.append(u"Pro Sound Effects")
        tags.append(u"PSE")
        tags.append(u"hybrid library")        
        tags.append(this_tag)
        file_path = (os.path.join(root, name))
        m = Media(name=name, category=6, assigned=1, tags=",".join(tags), thumbnail="")
        db.session.add(m)
        db.session.commit() 
        mid = m.id
        upload_path = r"//mcd-one/database/mcd_db/sfx/%08d" % int(mid)            
        if not os.path.exists(upload_path):
            os.mkdir(upload_path)

        shutil.copyfile(file_path, upload_path + "/" + name)
        print name
        print tags

#%%
if __name__ == '__main__':

    q = multiprocessing.Queue()
    
    for root, dirs, files in os.walk(this_path, topdown=False):
        files = [ fi for fi in files if fi.endswith((".mp3",".wav",".ogg")) ]
        for name in files:
            q.put([name, root])
    procs = []
    for i in range(0,4):
        proc = multiprocessing.Process(target=addFile, args=(q,))
        procs.append(proc)
        proc.start()
