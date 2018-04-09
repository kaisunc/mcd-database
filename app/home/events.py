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


@socketio.on('ajax_socket')
def ajax_socket(*args):
    '''
    main entry point for displaying datatables
    settings = {u'search': {u'regex': False, u'value': u''}, u'draw': 1, u'start': 0, u'length': 20, u'order': [{u'column': 1, u'dir': u'desc'}], u'columns': [{u'orderable': False, u'search': {u'regex': False, u'value': u''}, u'data': u'select-checkbox', u'name': u'', u'searchable': True}, {u'orderable': True, u'search': {u'regex': False, u'value': u''}, u'data': u'id', u'name': u'', u'searchable': True}, {u'orderable': True, u'search': {u'regex': False, u'value': u''}, u'data': u'name', u'name': u'', u'searchable': True}, {u'orderable': True, u'search': {u'regex': False, u'value': u''}, u'data': u'category', u'name': u'', u'searchable': True}, {u'orderable': True, u'search': {u'regex': False, u'value': u''}, u'data': u'timestamp', u'name': u'', u'searchable': True}, {u'orderable': True, u'search': {u'regex': False, u'value': u''}, u'data': u'assigned', u'name': u'', u'searchable': True}, {u'orderable': True, u'search': {u'regex': False, u'value': u''}, u'data': u'url', u'name': u'', u'searchable': True}, {u'orderable': True, u'search': {u'regex': False, u'value': u''}, u'data': u'tags', u'name': u'', u'searchable': True}, {u'orderable': True, u'search': {u'regex': False, u'value': u''}, u'data': u'description', u'name': u'', u'searchable': True}, {u'orderable': True, u'search': {u'regex': False, u'value': u''}, u'data': u'thumbnail', u'name': u'', u'searchable': True}]}
    settings = {u'search': {u'regex': False, u'value': u''}, u'draw': 2, u'start': 0, u'length': 20, u'order': [{u'column': 2, u'dir': u'asc'}], u'columns': [{u'orderable': False, u'search': {u'regex': False, u'value': u''}, u'data': u'select-checkbox', u'name': u'', u'searchable': True}, {u'orderable': True, u'search': {u'regex': False, u'value': u''}, u'data': u'id', u'name': u'', u'searchable': True}, {u'orderable': True, u'search': {u'regex': False, u'value': u''}, u'data': u'name', u'name': u'', u'searchable': True}, {u'orderable': True, u'search': {u'regex': False, u'value': u''}, u'data': u'category', u'name': u'', u'searchable': True}, {u'orderable': True, u'search': {u'regex': False, u'value': u''}, u'data': u'timestamp', u'name': u'', u'searchable': True}, {u'orderable': True, u'search': {u'regex': False, u'value': u''}, u'data': u'assigned', u'name': u'', u'searchable': True}, {u'orderable': True, u'search': {u'regex': False, u'value': u''}, u'data': u'url', u'name': u'', u'searchable': True}, {u'orderable': True, u'search': {u'regex': False, u'value': u''}, u'data': u'tags', u'name': u'', u'searchable': True}, {u'orderable': True, u'search': {u'regex': False, u'value': u''}, u'data': u'description', u'name': u'', u'searchable': True}, {u'orderable': True, u'search': {u'regex': False, u'value': u''}, u'data': u'thumbnail', u'name': u'', u'searchable': True}]}

    columns = [{u'mData': u'select-checkbox', u'data': u'select-checkbox'}, {u'mData': u'id', u'data': u'id'}, {u'mData': u'name', u'data': u'name'}, {u'mData': u'category', u'data': u'category'}, {u'mData': u'timestamp', u'data': u'timestamp'}, {u'mData': u'assigned', u'data': u'assigned'}, {u'mData': u'url', u'data': u'url'}, {u'mData': u'tags', u'data': u'tags'}, {u'mData': u'description', u'data': u'description'}, {u'mData': u'thumbnail', u'data': u'thumbnail'}]

    '''
    namespace = args[0]['namespace']
    settings = args[0]['settings']
    columns = args[0]['columns']
    columnDefs = args[0]['columnDefs']
    fields = args[0]['fields']
    lower = False

    model = getModel(namespace)
    items = model.query.all()

    start = int(settings['start'])
    length = int(settings['length'])
    sort_column = int(settings['order'][0]['column']) # column number
    sort_column_name = columns[sort_column]['data'] # column name
    sort_direction = settings['order'][0]['dir']

    def is_reverse(str_direction):
        ''' Maps the 'desc' and 'asc' words to True or False. '''
        return True if str_direction == 'desc' else False

    dt_data = []
    for row in items:
        dt_data.append(row.as_dict1(fields))
    recordsTotal = len(dt_data)

    for f in fields:
        if f['d_type'] == 'integer':
            lower = False
        else:
            lower = True

    if lower == True:        
        dt_data = sorted(dt_data, key=lambda x: x['name'].lower(), reverse=is_reverse(sort_direction))
    else:
        dt_data = sorted(dt_data, key=lambda x: x['name'], reverse=is_reverse(sort_direction))



    # if search returns only one page
    if len(dt_data) <= length:
        # display only one page
        dt_data = dt_data[start:]
    else:
        limit = -len(dt_data) + start + length
        if limit < 0:
            # display pagination
            dt_data = dt_data[start:limit]
        else:
            # display last page of pagination
            dt_data = dt_data[start:]

    t = json.dumps({"draw": settings['draw'], "recordsTotal": recordsTotal, "recordsFiltered": recordsTotal, "data": dt_data})
    emit('init_response', t, broadcast=False)

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

# if category is in use by any media, can't delete
@socketio.on('remove')
def remove(*args):
    namespace = ""
    if len(args) != 0:
        namespace = args[0]["namespace"]
        ids = args[0]["ids"]

    db.session.flush()
    model = getModel(namespace)

    for i in ids:
        delete = model.query.filter_by(id=i).one()
        db.session.delete(delete)
    db.session.commit()
    try:
        ids = json.dumps(ids)
        emit('delete_response', {'ids': ids}, broadcast=True)
    except:
        print 'something wrong'
