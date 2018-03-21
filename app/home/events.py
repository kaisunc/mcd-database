from flask import session, json
from flask_socketio import emit, join_room, leave_room
from .. import db, socketio
#from ..models import Project, Status, Asset, Shot, Task
from ..models import *
import copy
# match columns to model and match dt column name to db column name
# column name is USUALLY matched to model name, but not always. ie. assigned > user

# fields == input form fields
# columns == simple list of columns
# column def == json descriptor of columns

fields = []
@socketio.on('init')
def init(*args):
    global fields
    namespace = ""
    if len(args) != 0:
        namespace = args[0]["namespace"]

    model = getModel(namespace)
    items = model.query.all()

    fields = []
    ignore = ["id", "timestamp"]
    for column in items[0].__table__.columns.items():
        if column[0] == "id":
            pass
        else:
            col ={}
            col['name'] = column[0]
            col['label'] = column[0].title()

            if str(column[1].type) == "TEXT":
                col["type"] = "text"
            elif str(column[1].type) == "DATETIME":
                col["type"] = "datetime"
            elif str(column[1].type) == "INTEGER":
                if len(column[1].foreign_keys) == 1:
                    col['type'] = "select"
                    model = [m.target_fullname for m in column[1].foreign_keys][0].split(".")[0]
                    options = asOptions(model)
                    col['options'] = options
                else:
                    col["type"] = "text"

            fields.append(col)

    dt_data = []
    for row in items:
        dt_data.append(row.as_dict())

    headers = items[0].__table__.columns.keys()
    headers.insert(0, "select-checkbox")

    columnDefs = []
    columns = []
    for idx, header in enumerate(headers):
        if header == "select-checkbox":
            columnDef = {"width": "3%", "orderable": False, "className": header, "title": header, "targets": idx}
        else:
            columnDef = {"orderable": True, "className": header, "title": header, "targets": idx}
        column = {"data": header}
        columnDefs.append(columnDef)
        columns.append(column)

    columnDefs = json.dumps(columnDefs)
    columns = json.dumps(columns) #
    fields = json.dumps(fields) # input fields and type
    dt_data = json.dumps(dt_data)

    emit('init_response', {'data': dt_data, 'columns': columns, 'columnDefs': columnDefs, 'fields': fields}, broadcast=False)

@socketio.on('create')
def create(*args):
    namespace = ""
    if len(args) != 0:
        namespace = args[0]["namespace"]
        data = args[0]["data"]

    model = getModel(namespace)
    update = model()

    for f,v in data.items():
        setattr(update, f, v)

    db.session.add(update)
    db.session.flush()
    pid = update.id
    name = update.name

    for f, v in data.items():
        if f == 'process' and len(v) != 0:
            for t in v:
                task_model = getModel('task')
                task = task_model()
                setattr(task, 'process', t)
                setattr(task, 'parent_key', "%s_%08d" % (namespace, pid))
                setattr(task, 'name', name)
                db.session.add(task)

    db.session.commit()

    update = model.query.filter_by(id=pid).first()
    dt_data = json.dumps(update.as_dict())
    emit('add_response', {'data': dt_data}, broadcast=True)

@socketio.on('update')
def update(*args):
    global fields
    namespace = ""
    if len(args) != 0:
        namespace = args[0]["namespace"]
        pid = args[0]["id"]
        data = args[0]["data"]

    model = getModel(namespace)
    update = model.query.filter_by(id=pid).first()
    cols = update.__table__.columns.keys()

    db.session.flush()
    now = db.func.now()
    for k, v in data.iteritems():
        setattr(update, k, v)
        if 'timestamp' in cols:
            update.timestamp = now
    db.session.commit()

    update = model.query.filter_by(id=pid).first()
    #dt_data = convertDB(update, field_list)
    dt_data = json.dumps(update.as_dict())
    emit('update_response', {'data': dt_data}, broadcast=False)

@socketio.on('remove')
def remove(*args):
    namespace = ""
    if len(args) != 0:
        namespace = args[0]["namespace"]
        ids = args[0]["ids"]

    db.session.flush()
    model = getModel(namespace)

    for i in ids:
        delete = model.query.filter_by(id=i).first()
        print delete

    db.session.delete(delete)
    db.session.commit()
    try:
        ids = json.dumps(ids)
        emit('delete_response', {'ids': ids}, broadcast=True)
    except:
        #db.session.rollback()
        print 'something wrong'
