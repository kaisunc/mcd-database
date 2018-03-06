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

@login_manager.user_loader
def load_user(user_id):
    #return User.query.get(int(user_id))
    return User.query.get(int(user_id))
        