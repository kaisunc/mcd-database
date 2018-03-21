# https://flask-login.readthedocs.io/en/latest/
from flask_login import UserMixin # provides default flask login implementations
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager

class Datatable():
    def as_dict(self):
        t = {c.name: getattr(self, c.name) for c in self.__table__.columns}    
        t["select-checkbox"] = ""
        return t

    def as_dict1(self, fields):
        menus = []
        for f in fields:
            if f['type'] == 'select':
                menus.append(f)        

        temp = {}
        for c in self.__table__.columns:
            temp[c.name] = getattr(self, c.name)
            for menu in menus:
                if c.name == menu['name']:
                    for opt in menu['options']:
                        if getattr(self, c.name) == opt['value']:
                            temp[c.name] = opt

        temp["select-checkbox"] = ""
        return temp

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), index=True, unique=True)
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

    # def __repr__(self):
    #     return '<User: {}>'.format(self.username)

class Media(db.Model, Datatable):
    __tablename__ = 'media'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    category = db.Column(db.Integer, db.ForeignKey('category.id'))
    timestamp = db.Column(db.DateTime(), server_default=db.func.now(), server_onupdate=db.func.now())
    assigned = db.Column(db.Integer, db.ForeignKey('user.id'))
    url = db.Column(db.Text())
    tags = db.Column(db.Text())
    description = db.Column(db.Text())

class Category(db.Model, Datatable):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())    
    name_chn = db.Column(db.Text())

@login_manager.user_loader
def load_user(user_id):
    #return User.query.get(int(user_id))
    return User.query.get(int(user_id))

def getModel(selector):
    if selector == "media":
        model = Media
    elif selector == "category":
        model = Category
    elif selector == "user":
        model = User          
    else:
        return False
    return model

def asOptions(namespace):
    model = getModel(namespace)
    items = model.query.all()
    options = []
    for option in items:
        data = {"label": option.name, "value": option.id}
        options.append(data)
    return options    