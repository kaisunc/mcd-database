# -*- coding: utf-8 -*-
import os, operator, jinja2, urllib
from flask import flash, request, redirect, render_template, url_for, json, send_from_directory, send_file, make_response
from flask_login import login_required, current_user
from werkzeug import secure_filename
from .. import base_path
from ..models import *
from . import home

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

def nameValue(fields, category_filter):
    for f in fields:
        if f['name'] == 'category':
            for o in f['options']:
                if o['label'] == category_filter:
                    category_filter = o['value']    
        if category_filter == 'upload':
            category_filter = 0
    return category_filter  

@home.route('/')
def homepage():
    return redirect(url_for('home.media'))


# @home.route('/media/<category_filter>', defaults={'page': 1})
# @home.route('/media/<category_filter>/<page>', methods=['GET'])    
@home.route('/media', defaults={'category_filter': 4})    
@home.route('/media/<category_filter>', methods=['GET'])    
@login_required
def media(category_filter):
    namespace = "media"
    model = getModel(namespace)
    fields, columns, columnDefs = getFields(model)

    ff = fields # for dropzone dropdown menu selection
    category_filter = nameValue(fields, category_filter)

    # items = model.query.filter_by(category=category_filter).all()
    # tags = {}
    # for item in items:
    #     for tag in item.tags.split(","):
    #         if tag in tags:
    #             tags[tag] = tags[tag] + 1
    #         else:
    #             tags[tag] = 1
    
    # tags = sorted(tags.items(), key=operator.itemgetter(1), reverse=True)          

    return render_template('home/media.html', title='Media', namespace=namespace, columns=columns, columnDefs=columnDefs, fields=fields, ff=ff,category_filter=category_filter)

@home.route('/category', methods=['GET'])
@login_required
def category():
    namespace = "category"
    model = getModel(namespace)
    fields, columns, columnDefs = getFields(model)
    return render_template('home/tables.html', title='Category', namespace=namespace, columns=columns, columnDefs=columnDefs, fields=fields)

@home.route('/user', methods=['GET'])
@login_required
def user():
    namespace = "user"
    model = getModel(namespace)
    fields, columns, columnDefs = getFields(model)
    return render_template('home/tables.html', title='User', namespace=namespace, columns=columns, columnDefs=columnDefs, fields=fields)

@home.route('/logs', methods=['GET'])
@login_required
def logs():
    namespace = "logs"
    model = getModel(namespace)
    fields, columns, columnDefs = getFields(model)
    return render_template('home/tables.html', title='Logs', namespace=namespace, columns=columns, columnDefs=columnDefs, fields=fields)


@home.route('/ajax', methods=['GET'])
@login_required
def ajax(*args):
    params = request.args.to_dict()
    namespace = params['namespace']
    search = params["search[value]"]

    model = getModel(namespace)    
    fields, columns, columnDefs = getFields(model)
    items = model.query.order_by(model.id.desc()).limit(100000)

    start = int(params['start'])
    length = int(params['length'])

    sort_column = int(params['order[0][column]']) # column number
    sort_column_name = columns[sort_column]['data'] # column name
    sort_direction = params['order[0][dir]']

    dt_data = []
    for row in items:
        dt_data.append(row.as_dict1(fields))
    recordsTotal = len(dt_data)

    dt_data = custom_sort(dt_data, fields, sort_column_name, sort_direction)
    dt_data = custom_paging(dt_data, start, length)


    t = json.dumps({"draw": params['draw'], "recordsTotal": recordsTotal, "recordsFiltered": recordsTotal, "data": dt_data})
    return t


@home.route('/upload', methods=['POST'])
@login_required
def upload():
    print 'counting requests'
    print request.args
    if request.method == 'POST':    
        fs = request.files.to_dict()
        for k,v in fs.items():
            f = request.files[k]
            category  = request.args.get('category')
            file_id = int(request.args.get('file_id'))
            folder_path = "%s/%s/%08d" % (base_path, category, file_id)

            if os.path.isdir(folder_path) is False:
                os.makedirs(folder_path)
            file_path = "%s/%s" % (folder_path, f.filename)            
            f.save(file_path)
            return "ok"

    # if request.method == 'POST':    
    #     fs = request.files.to_dict()
    #     for k,v in fs.items():
    #         f = request.files[k]
    #         folder_path = "%s/upload_temp" % (base_path)
    #         file_path = "%s/%s" % (folder_path, f.filename)            
    #         f.save(file_path)
    #         print "saved" + k
    #     return "ok"        

    # if request.method == 'POST':
    #     f = request.files['file']
    #     category  = request.args.get('category')
    #     file_id = int(request.args.get('file_id'))
    #     folder_path = "%s/%s/%08d" % (base_path, category, file_id)

    #     if os.path.isdir(folder_path) is False:
    #         os.makedirs(folder_path)
    #     file_path = "%s/%s" % (folder_path, f.filename)            
    #     f.save(file_path)
    #     return "ok"

# @home.route('/download/<category>/<file_id>/<string:filename>', methods=['GET', 'POST']) 
# @login_required 
# def download(category, file_id, filename): 
#     directory = "%s/%s/%s" % (base_path, category, str(file_id)) 
#     return send_from_directory(directory=directory, filename=unicode(filename), as_attachment=True)

@home.route('/download', methods=['GET', 'POST']) 
@login_required 
def download(): 
    params = request.args.to_dict()

    category = params['category']
    file_id = params['file_id']
    filename = params['filename']

    out_file = "%s/%s/%s/%s" % (base_path, category, str(file_id), filename) 

    response = make_response(send_file(out_file, conditional=True)) # conditional makes video/audio seeking possible, read http 206 partial content
    response.headers["Content-Disposition"] = "attachment; filename*=UTF-8''{utf_filename}".format(utf_filename=urllib.quote(filename.encode('utf-8')))

    return response

@home.route('/download_zip', methods=['GET', 'POST'])
@login_required
def download_zip():
    unique_filename = request.form.to_dict()["uid"].replace("\"","")
    filename = base_path + "/upload_temp/" + unique_filename
    return send_file(filename, attachment_filename="files.zip", as_attachment=True)
