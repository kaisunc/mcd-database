# https://flask-login.readthedocs.io/en/latest/
from flask_login import UserMixin # provides default flask login implementations
from werkzeug.security import generate_password_hash, check_password_hash
import re
from app import db, login_manager

class Datatable():
    # format row as datatable readable json
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
    is_admin = db.Column(db.Boolean, default=False)


    @property
    def password(self):
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class Media(db.Model, Datatable):
    __tablename__ = 'media'
    __searchable__ = ['name', 'tags']

    thumbnail = db.Column(db.Text())
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    category = db.Column(db.Integer, db.ForeignKey('category.id'))
    timestamp = db.Column(db.DateTime(), server_default=db.func.now(), server_onupdate=db.func.now())
    assigned = db.Column(db.Integer, db.ForeignKey('user.id'))
    tags = db.Column(db.Text())
    description = db.Column(db.Text())



class Category(db.Model, Datatable):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())    
    name_chn = db.Column(db.Text())

@login_manager.user_loader
def load_user(user_id):
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

# this MAY need to be customized for each model, it might not be possible to adapt all models.
# write a js script to modify each model and jinja insert to appropriate page
def getFields(model):
    fields = []
    columns = []
    columnDefs = []
    idx = 0
    text_types = ["TEXT", "VARCHAR"]
    

    # customize dt columns here, either automate or static define 
    for column in model.__table__.columns.items():
        idx = idx + 1
        columns.append({"data": column[0]})
        columnDef = {"orderable": True, "className": column[0] + " text-center", "title": column[0], "targets": idx}
        columnDefs.append(columnDef)

        col ={}
        noedit_fields = ["id", "thumbnail", "timestampe"] #name is no edit, but needs to be appended to fields
        if column[0] in noedit_fields: # no form input for id
            pass
        else:
            col['name'] = column[0]
            col['label'] = column[0].title()

            if re.sub(r'\([^)]*\)', '',  str(column[1].type)) in text_types:
                if column[0] == "tags":
                    col["type"] = "text"
                    col["d_type"] = "text"    
                else:
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
                    columns[-1]['render'] = "category_render" # keyword render will assign js render function
                else:
                    col["type"] = "text"

            fields.append(col)

    columns.insert(0, {"data": "select-checkbox"})
    columnDefs.insert(0, {"width": "3%", "orderable": False, "className": "select-checkbox", "title": "select-checkbox", "targets": 0})
    return fields, columns, columnDefs

def is_reverse(str_direction):
    ''' Maps the 'desc' and 'asc' words to True or False. '''
    return True if str_direction == 'desc' else False

def custom_sort(data, fields, sort_column_name, sort_direction):
    lower = False
    for f in fields:
        if f['name'] == sort_column_name:
            if f['d_type'] == 'integer':
                lower = False
            elif f['d_type'] == 'text':
                lower = True

    if lower == True:
        data = sorted(data, key=lambda x: x[sort_column_name].lower(), reverse=is_reverse(sort_direction))
    else:
        data = sorted(data, key=lambda x: x[sort_column_name], reverse=is_reverse(sort_direction))

    return data    

def custom_paging(data, start, length):
    # if search returns only one page
    if len(data) <= length:
        # display only one page
        data = data[start:]
    else:
        limit = -len(data) + start + length
        if limit < 0:
            # display pagination
            data = data[start:limit]
        else:
            # display last page of pagination
            data = data[start:]
    return data    

  