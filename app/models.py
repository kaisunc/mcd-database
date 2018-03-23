# https://flask-login.readthedocs.io/en/latest/
from flask_login import UserMixin # provides default flask login implementations
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager

class Datatable():
    def dt_data_row(self):
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

def getOptions(namespace):
    model = getModel(namespace)
    items = model.query.all()
    options = []
    for option in items:
        data = {"label": option.name, "value": option.id}
        options.append(data)
    return options    

def getFields(model):
    fields = []
    columns = []
    columnDefs = []
    idx = 0
    ignore = ["id", "timestamp"]
    for column in model.__table__.columns.items():
        idx = idx + 1
        columns.append({"data": column[0]})
        columnDef = {"orderable": True, "className": column[0], "title": column[0], "targets": idx}
        columnDefs.append(columnDef)

        col ={}
        if column[0] == "id": # no form input for id
            pass
        else:
            col['name'] = column[0]
            col['label'] = column[0].title()

            if str(column[1].type) == "TEXT":
                col["type"] = "text"
            elif str(column[1].type) == "DATETIME":
                col["type"] = "datetime"
            elif str(column[1].type) == "INTEGER":
                if len(column[1].foreign_keys) == 1:
                    col['type'] = "select"
                    fk_model = [m.target_fullname for m in column[1].foreign_keys][0].split(".")[0]
                    options = getOptions(fk_model)
                    col['options'] = options
                else:
                    col["type"] = "text"

            fields.append(col)

    columns.insert(0, {"data": "select-checkbox"})
    columnDefs.insert(0, {"width": "3%", "orderable": False, "className": "select-checkbox", "title": "select-checkbox", "targets": 0})
    return fields, columns, columnDefs

    