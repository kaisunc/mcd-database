import os
from flask import flash, request, redirect, render_template, url_for, json
from flask_login import login_required
from werkzeug import secure_filename
import jinja2

from ..models import *

from . import home
from . import events
from events import *
# from forms import AddProjectForm, AddStatusForm
# from .. import db
# from ..models import Project, Status, Asset
_js_escapes = {
        '\\': '\\u005C',
        '\'': '\\u0027',
        '"': '\\u0022',
        '>': '\\u003E',
        '<': '\\u003C',
        '&': '\\u0026',
        '=': '\\u003D',
        '-': '\\u002D',
        ';': '\\u003B',
        u'\u2028': '\\u2028',
        u'\u2029': '\\u2029'
}
# Escape every ASCII character with a value less than 32.
_js_escapes.update(('%c' % z, '\\u%04X' % z) for z in xrange(32))
def jinja2_escapejs_filter(value):
        value = json.dumps(value)
        retval = []
        for letter in value:
                if _js_escapes.has_key(letter):
                        retval.append(_js_escapes[letter])
                else:
                        retval.append(letter)

        return jinja2.Markup("".join(retval))

@home.route('/')
def homepage():
    return render_template('home/index.html', title="Welcome")

@home.route('/media', methods=['GET'])    
@login_required
def media():
    namespace = "media"
    model = getModel(namespace)
    items = model.query.all()
    fields, columns, columnDefs = getFields(model)
    ff = fields
    columns = jinja2_escapejs_filter(columns)
    columnDefs = jinja2_escapejs_filter(columnDefs)
    fields = jinja2_escapejs_filter(fields)
    
    return render_template('home/table.html', title='Media', namespace=namespace, columns=columns, columnDefs=columnDefs, fields=fields, ff=ff)


@home.route('/category', methods=['GET'])
@login_required
def category():
    namespace = "category"
    model = getModel(namespace)
    items = model.query.all()
    fields, columns, columnDefs = getFields(model)

    columns = jinja2_escapejs_filter(columns)
    columnDefs = jinja2_escapejs_filter(columnDefs)
    fields = jinja2_escapejs_filter(fields)
    return render_template('home/table.html', title='Category', namespace=namespace, columns=columns, columnDefs=columnDefs, fields=fields)

    #namespace = "category"
    #return render_template('home/table.html', title='Category', namespace=namespace, db_filter="")

@home.route('/user', methods=['GET'])
@login_required
def user():
    namespace = jinja2_escapejs_filter("user")
    return render_template('home/table.html', title='Users', namespace=namespace)


@home.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        base_path = "C:/Users/julio/source"
        f = request.files['file']
        print request
        category  = request.args.get('category')
        file_id = request.args.get('file_id')
        folder_path = "%s/%s/%s" % (base_path, category, file_id)

        if os.path.isdir(folder_path) is False:
            os.makedirs(folder_path)
        file_path = "%s/%s" % (folder_path, f.filename)            
        f.save(file_path)
        return "ok"

@home.route('/ajax', methods=['GET'])
def ajax():
    params = request.args.to_dict()
    print params

    namespace = "media"
    model = getModel(namespace)
    items = model.query.all()
    fields, columns, columnDefs = getFields(model)

    dt_data = []
    for row in items:
        dt_data.append(row.as_dict1(fields))
    t = {"data": dt_data}
    return json.dumps(t)
