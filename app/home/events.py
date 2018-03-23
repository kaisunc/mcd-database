from flask import session, json
from flask_socketio import emit, join_room, leave_room
from .. import db, socketio

from ..models import *

'''
fields
target: editor
input: model name, no query
output: list of fields that can be edited in datatables
notes: ignore fields that does not need to be edited, select fields will sub query

columns
target: table
input: header
ouput: list of columns and its data type

column def
target: table
input: header
output: list similar to columns, contains css properties

dt_data
taget: table
input: model items
output: json data, {key: '', value: ''}

options
target: editor, select menu(select, radio)
input: model name, query model
output: json list, {label: '', value: ''}

'''
fields = []
@socketio.on('init')
def init(*args):
    namespace = ""
    if len(args) != 0:
        namespace = args[0]["namespace"]

    model = getModel(namespace)
    items = model.query.all()
    fields, columns, columnDefs = getFields(model)

    dt_data = []
    for row in items:
        #dt_data.append(row.dt_data_row())
        dt_data.append(row.as_dict1(fields))

    columnDefs = json.dumps(columnDefs)
    columns = json.dumps(columns) #
    fields = json.dumps(fields) # input fields and type
    dt_data = json.dumps(dt_data)

    emit('init_response', {'data': dt_data, 'columns': columns, 'columnDefs': columnDefs, 'fields': fields}, broadcast=False)

@socketio.on('create')
def create(*args):
    namespace = ""
    pids = []
    if len(args) != 0:
        namespace = args[0]["namespace"]
        data = args[0]["data"]
        try:
            multiple = args[0]["multiple"]
        except:
            pass

    model = getModel(namespace)
    fields, columns, columnDefs = getFields(model)    
    if multiple == 'true':
        for d in data:
            update = model()
            for k,v in d.iteritems():
                setattr(update, k, v)
            db.session.add(update)
            db.session.flush()
            pids.append(update.id)

        db.session.commit()

        update = model.query.filter(model.id.in_(pids)).all()
        output = []
        for x in update:
            dt_data = json.dumps(x.as_dict1(fields))
            emit('add_response', {'data': dt_data}, broadcast=True)

    else:
        update = model()

        for k,v in data.iteritems():
            setattr(update, k, v)


        db.session.add(update)
        db.session.flush()
        pid = update.id

        db.session.commit()

        update = model.query.filter_by(id=pid).first()
        dt_data = json.dumps(update.as_dict1(fields))
        emit('add_response', {'data': dt_data}, broadcast=True)

@socketio.on('update')
def update(*args):
    namespace = ""
    if len(args) != 0:
        namespace = args[0]["namespace"]
        pid = args[0]["id"]
        data = args[0]["data"]

    model = getModel(namespace)
    fields, columns, columnDefs = getFields(model)
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
    #dt_data = json.dumps(update.dt_data_row())

    dt_data = json.dumps(update.as_dict1(fields))
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
        db.session.delete(delete)
    db.session.commit()
    try:
        ids = json.dumps(ids)
        emit('delete_response', {'ids': ids}, broadcast=True)
    except:
        #db.session.rollback()
        print 'something wrong'
