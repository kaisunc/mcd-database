import os
from flask import flash, request, redirect, render_template, url_for, json, send_from_directory
from flask_login import login_required
from werkzeug import secure_filename
import jinja2
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

@home.route('/')
def homepage():
    return render_template('home/index.html', title="Welcome")

@home.route('/media/<category_filter>', methods=['GET'])    
@login_required
def media(category_filter):
    namespace = "media"
    model = getModel(namespace)
    fields, columns, columnDefs = getFields(model)
    print columns
    ff = fields # for dropzone dropdown menu selection
    for c in enumerate(columns):
        if c[1]['data'] == 'thumbnail':
            if category_filter == 'images':
                c[1]['render'] = "thumb_render"    
            elif category_filter == 'sfx' or category_filter == 'music':
                c[1]['render'] = "sound_render"    
            elif category_filter == "videos" or category_filter == "tutorial":
                c[1]['render'] = "video_render"    
            elif category_filter == "fonts":
                c[1]['render'] = "font_render"                    
            else:
                c[1]['render'] = "thumb_render"


    if category_filter == 'upload':
        return render_template('home/upload.html', title='Media', namespace=namespace, columns=columns, columnDefs=columnDefs, fields=fields, ff=ff, category_filter=category_filter)
    else:
        return render_template('home/media.html', title='Media', namespace=namespace, columns=columns, columnDefs=columnDefs, fields=fields, ff=ff, category_filter=category_filter)

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
    return render_template('home/upload.html', title='Category', namespace=namespace, columns=columns, columnDefs=columnDefs, fields=fields, category_filter='upload')

@home.route('/user', methods=['GET'])
@login_required
def user():
    namespace = jinja2_escapejs_filter("user")
    return render_template('home/table.html', title='Users', namespace=namespace)

@home.route('/ajax', methods=['GET'])
@login_required
def ajax():
    params = request.args.to_dict()

    namespace = "media"
    model = getModel(namespace)
    items = model.query.all()
    fields, columns, columnDefs = getFields(model)

    dt_data = []
    for row in items:
        dt_data.append(row.as_dict1(fields))
    t = {"data": dt_data}
    return json.dumps(t)

@home.route('/upload', methods=['POST'])
@login_required
def upload():
    if request.method == 'POST':
        f = request.files['file']
        category  = request.args.get('category')
        file_id = int(request.args.get('file_id'))
        folder_path = "%s/%s/%08d" % (base_path, category, file_id)

        if os.path.isdir(folder_path) is False:
            os.makedirs(folder_path)
        file_path = "%s/%s" % (folder_path, f.filename)            
        f.save(file_path)
        return "ok"

@home.route('/download/<category>/<file_id>/<string:filename>', methods=['GET', 'POST'])
@login_required
def download(category, file_id, filename):
    base  = "C:/Users/julio/Dropbox/Projects/mcd_database/assets"
    directory = "%s/%s/%s" % (base, category, str(file_id))
    return send_from_directory(directory=directory, filename=filename)
