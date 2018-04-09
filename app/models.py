# https://flask-login.readthedocs.io/en/latest/
from flask_login import UserMixin # provides default flask login implementations
from werkzeug.security import generate_password_hash, check_password_hash
import re
from app import db, login_manager


class Datatable():
    def dt_data_row(self):
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
    thumbnail = db.Column(db.Text())


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

        if column[0] == "thumbnail":
            columns[-1]['render'] = "thumb_render"

        col ={}
        if column[0] == "id": # no form input for id
            pass
        else:
            col['name'] = column[0]
            col['label'] = column[0].title()

            if str(column[1].type) == "TEXT":
                col["type"] = "text"
                col["d_type"] = "text"
            elif str(column[1].type) == "DATETIME":
                col["type"] = "datetime"
                col["d_type"] = "datetime"
            elif str(column[1].type) == "INTEGER":
                col["d_type"] = "integer"
                if len(column[1].foreign_keys) == 1:
                    col['type'] = "select"
                    fk_model = [m.target_fullname for m in column[1].foreign_keys][0].split(".")[0]
                    options = getOptions(fk_model)
                    col['options'] = options
                    columns[-1]['render'] = "render" # keyword render will assign js render function

                else:
                    col["type"] = "text"

            fields.append(col)

    columns.insert(0, {"data": "select-checkbox"})
    columnDefs.insert(0, {"width": "3%", "orderable": False, "className": "select-checkbox", "title": "select-checkbox", "targets": 0})
    return fields, columns, columnDefs

    