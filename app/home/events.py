from flask import session, json
from flask_socketio import emit, join_room, leave_room
from shutil import rmtree
import base64, os
from PIL import Image
from io import BytesIO
from .. import db, socketio
from .. import base_path
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
    category_filter = args[0]['category_filter']
    fields = args[0]['fields']
    search = settings['search']['value']
    model = getModel(namespace)
    print category_filter
    if category_filter != 0:
        if search == "":
            items = model.query.filter_by(category=category_filter).order_by(model.id.desc()).limit(100000)
        else:
            items = model.query.filter_by(category=category_filter).whoosh_search(search).all()
    else:
        if search == "":
            items = model.query.order_by(model.id.desc()).limit(1000)
        else:
            items = model.query.whoosh_search(search).all()

    start = int(settings['start'])
    length = int(settings['length'])
    sort_column = int(settings['order'][0]['column']) # column number
    sort_column_name = columns[sort_column]['data'] # column name
    sort_direction = settings['order'][0]['dir']

    dt_data = []
    for row in items:
        dt_data.append(row.as_dict1(fields))
    recordsTotal = len(dt_data)

    dt_data = custom_sort(dt_data, fields, sort_column_name, sort_direction)
    dt_data = custom_paging(dt_data, start, length)


    t = json.dumps({"draw": settings['draw'], "recordsTotal": recordsTotal, "recordsFiltered": recordsTotal, "data": dt_data})
    emit('init_response', t, broadcast=False)

fields = []
@socketio.on('init')
def init(*args):
    if len(args) != 0:
        namespace = args[0]["namespace"]

    model = getModel(namespace)

    items = model.query.limit(10000).all()
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
    '''
    Single and Multiple Modes using boolean "multiple"
    '''
    def decode_base64(data):
        data = data.split(",")[-1]
        missing_padding = len(data) % 4
        if missing_padding != 0:
            data += b'='* (4 - missing_padding)
        return base64.decodestring(data)

    def addRow(d):
        update = model()
        for k,v in d.iteritems():
            setattr(update, k, v)
        db.session.add(update)
        db.session.flush()
        return update

    namespace = ""
    pids = []
    if len(args) != 0:
        namespace = args[0]["namespace"]
        data = args[0]["data"]
        thumbs = args[0]["thumbs"]
        try:
            multiple = args[0]["multiple"]
        except:
            pass

    model = getModel(namespace)
    fields, columns, columnDefs = getFields(model)
    if multiple == 'true':
        for d in data:
            update = addRow(d)
            pids.append(update.id)

        db.session.commit()

        update = model.query.filter(model.id.in_(pids)).all()
        output = []
        for item in update:
            item = item.as_dict1(fields)
            item_id = item['id']
            item_name = item['name']
            item_category = item['category']
            dt_data = json.dumps(item)

            for thumb in thumbs:
                if thumb['name'] == item_name:
                    # t = decode_base64(thumb['thumb'])
                    t = thumb['thumb'].split(",")[-1]
                    thumb_path = "%s/%s/%08d" % (base_path, item_category['label'], item_id)
                    if os.path.isdir(thumb_path) is False:
                        os.makedirs(thumb_path)

                    im = Image.open(BytesIO(base64.b64decode(t)))
                    im.save(thumb_path + "/thumb.jpg", "JPEG", quality=80, optimize=True)

            emit('add_response', {'data': dt_data}, broadcast=True)

    # else:
    #     update = addRow(data)
    #     pid = update.id

    #     db.session.commit()

    #     update = model.query.filter_by(id=pid).first()
    #     dt_data = json.dumps(update.as_dict1(fields))
    #     emit('add_response', {'data': dt_data}, broadcast=True)

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

import time
# if category is in use by any media, can't delete
@socketio.on('remove')
def remove(*args):
    namespace = ""
    if len(args) != 0:
        namespace = args[0]["namespace"]
        ids = args[0]["ids"]

    db.session.flush()
    model = getModel(namespace)

    remove_list = []
    for i in ids:
        delete = model.query.filter_by(id=i).one()
        remove_list.append({'id': i, 'category': delete.category})
        db.session.delete(delete)
    db.session.commit()

    start = time.time()


    try:
        ids = json.dumps(ids)
        emit('delete_response', {'ids': ids}, broadcast=True)
        categories = Category.query.all()
        for remove in remove_list:
            file_id = remove['id']
            category_id = remove['category']
            category = [c.name for c in categories if c.id == category_id][0]
            remove_path = "%s/%s/%08d" % (base_path, category, int(file_id))
            rmtree(remove_path)
    except:
        print 'something wrong'
    end = time.time()
    print(end - start)
    return 'ok'


