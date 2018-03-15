# https://flask-login.readthedocs.io/en/latest/
from flask_login import UserMixin # provides default flask login implementations
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    #role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    is_admin = db.Column(db.Boolean, default=False)
    # projects = db.relationship('Project', backref='work_on', lazy='dynamic')
    # tasks = db.relationship('Task', backref='work_on', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User: {}>'.format(self.username)

class Media(db.Model):
    __tablename__ = 'media'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    media_type = db.Column(db.Integer, db.ForeignKey('media_type.id'))
    timestamp = db.Column(db.DateTime(), server_default=db.func.now(), server_onupdate=db.func.now())
    assigned = db.Column(db.Integer, db.ForeignKey('user.id'))
    url = db.Column(db.Text())
    tags = db.Column(db.Text())
    description = db.Column(db.Text())

class Media_Type(db.Model):
    __tablename__ = 'media_type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())    
    name_chn = db.Column(db.Text())

@login_manager.user_loader
def load_user(user_id):
    #return User.query.get(int(user_id))
    return User.query.get(int(user_id))
