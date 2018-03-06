from flask import session, json
from flask_socketio import emit, join_room, leave_room
from .. import db, socketio
#from ..models import Project, Status, Asset, Shot, Task
from ..models import *
import copy
# match columns to model and match dt column name to db column name
# column name is USUALLY matched to model name, but not always. ie. assigned > user
# 
model_prefs = [{'model': 'user', 'column': ['assigned'], 'choice':'username'}]   

# convert a db obj to datatables json data
def convertDB(obj, field_list):
    #status_choices = {option.id: option.name for option in Status.query.all()}
    # add or remove columns from model
    def massage(dbDict):
        newDB = {}
        for k,v in dbDict.iteritems():
            if k == "_sa_instance_state":
                continue
            for f in field_list:
                if k == f['name'] and f['type'] == 'select': # add options into datatable data
                    for pref in model_prefs:
                        if k in pref['column']:
                            model = getModel(pref['model'])
                            choices = {option.id: getattr(option, pref['choice'])  for option in model.query.all()}
                        else:
                            model = getModel(k)
                            choices = {option.id: option.name for option in model.query.all()}
                        if v != None:
                            v = choices[v]
                        else:
                            v = ""              
            newDB[k] = v
            newDB['select-checkbox'] = ""
        return newDB

    dt_data = []
    if type(obj) is list:
        for row in obj:
            dt_data.append(massage(row.__dict__))
    else:
        dt_data = massage(obj.__dict__)
    return json.dumps(dt_data)   


def getModel(selector):
    if selector == "project":
        model = Project
    elif selector == "status":
        model = Status
    elif selector == "asset":
        model = Asset
    elif selector == "shot":
        model = Shot   
    elif selector == "task":
        model = Task
    elif selector == "process":
        model = Process
    elif selector == "pipeline":
        model = Pipeline
    elif selector == "asset_type":
        model = AssetType
    elif selector == "assigned":
        model = User       
    elif selector == "user":
        model = User          
    else:
        return False
    return model

# gets from name, id from model
def getOptions(model, namespace):
    option_model = getModel(model)
    # not alway 'name', so need a way to specify custom columns to query from.
    options = []
    if namespace == "asset":
        option_model = option_model.query.filter(Process.pipeline == 1)
    elif namespace == "shot":
        option_model = option_model.query.filter(Process.pipeline == 2)
    else:
        option_model = option_model.query.all() 
    for option in option_model:
        if model == "assigned":
            label = getattr(option, "username")
        else:
            label = getattr(option, "name")        
        data = {"label": label, "value": option.id}
        options.append(data)
    return options

# fields == input form fields
# columns == simple list of columns
# column def == json descriptor of columns
@socketio.on('init')
def init(*args):
    namespace = ""
    if len(args) != 0:
        namespace = args[0]["namespace"]
        field_list = args[0]["field_list"]

    # dt_data
    model = copy.deepcopy(getModel(namespace))
    data = model.query.all()
    dt_data = convertDB(data, field_list)    

    fields = []
    for f in field_list:
        field = {'label': f['name'].title(), 'name': f['name']}
        if f['type'] == 'select' or f['type'] == 'checkbox':
            options = getOptions(f['name'], namespace)
            field = {'label': f['name'].title(), 'name':f['name'],'options': options, 'type': f['type']}
        elif f['type'] == 'inline':
            print 'inline'

        fields.append(field)
    headers = model.__table__.columns.keys()
    headers.insert(0, "select-checkbox")

    # columns and columnDef
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

    # append custom columns 
    columnDefs = json.dumps(columnDefs)
    columns = json.dumps(columns) # 
    fields = json.dumps(fields) # input fields and type

    emit('init_response', {'data': dt_data, 'columns': columns, 'columnDefs': columnDefs, 'fields': fields}, broadcast=False)


# 
@socketio.on('create')
def create(*args):
    namespace = ""
    if len(args) != 0:
        namespace = args[0]["namespace"]
        data = args[0]["data"]
        field_list = args[0]["field_list"]

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
    dt_data = convertDB(update, field_list)    

    emit('add_response', {'data': dt_data}, broadcast=True)

@socketio.on('update')    
def update(*args):
    namespace = ""
    if len(args) != 0:
        namespace = args[0]["namespace"]
        pid = args[0]["id"]
        data = args[0]["data"]
        field_list = args[0]["field_list"]

    model = getModel(namespace)
    update = model.query.filter_by(id=pid).first()
    cols = update.__table__.columns.keys()

    db.session.flush()
    now = db.func.now()
    for k, v in data.iteritems():
        setattr(update, k, v)
        if 'timestampe' in cols:
            update.timestamp = now
    db.session.commit()

    update = model.query.filter_by(id=pid).first()
    dt_data = convertDB(update, field_list)    
   
    emit('update_response', {'data': dt_data}, broadcast=True)

@socketio.on('remove')
def remove(*args):
    namespace = ""
    if len(args) != 0:
        namespace = args[0]["namespace"]
        ids = args[0]["ids"]

    model = getModel(namespace)

    for i in ids:
        model.query.filter_by(id=i).delete()
    db.session.commit()
    ids = json.dumps(ids)

    emit('delete_response', {'ids': ids}, broadcast=True)
