# -*- coding: utf-8 -*-
from flask import session, json, send_from_directory
from flask_login import current_user
from flask_socketio import emit, join_room, leave_room
from shutil import rmtree
import base64, os, operator, zipfile, uuid
from PIL import Image
import time, sys
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
    category_filter = int(args[0]['category_filter'])
    fields = args[0]['fields']
    search = settings['search']['value']
    model = getModel(namespace)        

    
    start = int(settings['start'])
    length = int(settings['length'])
    sort_column = int(settings['order'][0]['column']) # column number
    sort_column_name = columns[sort_column]['data'] # column name
    sort_direction = settings['order'][0]['dir']

    order_func = "%s.%s.%s()" % ("Media", sort_column_name, sort_direction)

    #print start
    
    if category_filter != 0:
        recordsTotal = model.query.filter_by(category=category_filter).count()        
        if search == "":
            items = model.query.filter_by(category=category_filter).order_by(eval(order_func)).offset(start).limit(length)
        else:
            items = model.query.filter_by(category=category_filter).order_by(eval(order_func)).whoosh_search(search)
            recordsTotal = sum(1 for _ in items)
            items = items.offset(start).limit(length)
    else:
        recordsTotal = model.query.count()                
        if search == "":
            items = model.query.order_by(eval(order_func)).offset(start).limit(length)
        else:
            items = model.query.whoosh_search(search).all()
            recordsTotal = sum(1 for _ in items)
            items = items.offset(start).limit(length)            

    dt_data = []
    for row in items:
        dt_data.append(row.as_dict1(fields))

    #dt_data = custom_sort(dt_data, fields, sort_column_name, sort_direction)
    #dt_data = custom_paging(dt_data, start, length)

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

@socketio.on('get_tags')
def get_tags(*args):
    namespace = args[0]["namespace"]
    category_filter = args[0]['category_filter']

    model = getModel(namespace)    
    items = model.query.filter_by(category=category_filter).all()
    tags = {}
    for item in items:
        for tag in item.tags.split(","):
            if tag in tags:
                tags[tag] = tags[tag] + 1
            else:
                tags[tag] = 1
    
    tags = sorted(tags.items(), key=operator.itemgetter(1), reverse=True)[0:100]
    tags_list = []
    for t in tags:
        tags_list.append({'tag':t[0], 'count':t[1]})    
    emit('tag_response', tags_list)
   
    #tags = [(u'fitness', 185), (u'poetry', 178), (u'dating', 175), (u'writing', 174), (u'business', 172), (u'inspiration', 172), (u'tips', 171), (u'uk', 170), (u'bible', 170), (u'love', 169), (u'homes', 169), (u'women', 167), (u'comedy', 167), (u'marketing', 166), (u'culture', 165), (u'landscape', 165), (u'music', 165), (u'blogging', 164), (u'life', 164), (u'photo', 163), (u'environment', 163), (u'philosophy', 162), (u'science', 161), (u'indie', 161), (u'film', 161), (u'dogs', 160), (u'comics', 160), (u'politics', 160), (u'religion', 159), (u'fashion', 159)]



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
        try:
            multiple = args[0]["multiple"]
        except:
            pass
        try:
            thumbs = args[0]["thumbs"]                        
        except:
            pass            

    model = getModel(namespace)
    #l = Logs(action="create", assigned=current_user.id, data=json.dumps(data))
    #db.session.add(l)
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
                    im = im.convert("RGB")
                    im.save(thumb_path + "/thumb.jpg", "JPEG", quality=80, optimize=True)

            output.append(dt_data)
        emit('add_response', {'data': json.dumps(output)}, broadcast=True)

    else:
        update = addRow(data)
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

    l = Logs(action="update", assigned=current_user.id, data=json.dumps(data))
    db.session.add(l)

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
    print 'removing'
    if len(args) != 0:
        ids = args[0]['ids']
        namespace = args[0]["namespace"]

    l = Logs(action="remove", assigned=current_user.id, data=json.dumps(ids))
    db.session.add(l)

    db.session.flush()
    model = getModel(namespace)

    remove_list = []
    for i in ids:
        delete = model.query.filter_by(id=i).one()
        try:
            remove_list.append({'id': i, 'category': delete.category})
        except:
            pass
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


@socketio.on('download_selected')
def download_selected(*args):
    oldwd = os.getcwd()

    data = args[0]['data']
    category_filter = args[0]['category_filter']
    unique_filename = str(uuid.uuid4()) + ".zip"

    zf = zipfile.ZipFile(base_path + '/upload_temp/' + unique_filename, mode='w')
    for d in data:
        file_path = "%s/%s/%08d" % (base_path, category_filter, int(d['id']))
        os.chdir(file_path)
        zf.write(d['name'])
    zf.close()
    emit('zipped', unique_filename)

@socketio.on('append_tags')
def append_tags(*args):
    data = args[0]['data']
    category_filter = args[0]['category_filter']
    append_tags = args[0]['append_tags'].split(",")
    namespace = "media"
    model = getModel(namespace)
    fields, columns, columnDefs = getFields(model)

    for d in data:
        tags = d['tags'].split(",")
        tags = tags + append_tags
        pid = d['id']
            
        update = Media.query.filter_by(id=pid).first()
        update.tags = ",".join(tags)
    db.session.commit()
    emit('append_tag_response', broadcast=False)