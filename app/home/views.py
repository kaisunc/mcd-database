
from flask import flash, request, redirect, render_template, url_for, json
from flask_login import login_required
from werkzeug import secure_filename
import jinja2

from ..models import Media_Type, Media

from . import home
from . import events
from events import *
# from forms import AddProjectForm, AddStatusForm
# from .. import db
# from ..models import Project, Status, Asset
_js_escapes = {
        '\\': '\\u005C',
        '\'': '\'',
        '"': '\"',
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
    namespace = jinja2_escapejs_filter("media")
    field_list = jinja2_escapejs_filter([{'name': 'name', 'type': 'text'}, {'name': 'media_type', 'type': 'select'}, {'name': 'url', 'type': 'text'}, {'name': 'tags', 'type': 'text'},{'name': 'assigned', 'type': 'select'}])
    hide = jinja2_escapejs_filter(['timestamp'])

    media_types = Media_Type.query.all()
    mt = []
    for t in media_types:
        data = {"name": t.name, "id": t.id}
        mt.append(data)

    return render_template('home/table.html', title='Database', namespace=namespace, field_list=field_list, hide=hide, data=mt)


@home.route('/media_type', methods=['GET'])
@login_required
def media_type():
    namespace = jinja2_escapejs_filter("media_type")
    field_list = jinja2_escapejs_filter([{'name': 'name', 'type': 'text'}, {'name': 'name_chn', 'type': 'text'}])    
    return render_template('home/table.html', title='Type', namespace=namespace, field_list=field_list, data='')

@home.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        f = request.files['file']
        #print f.filename
        #print secure_filename(f.filename)
        print type(f.filename)
        f.save(r"C:\\Users\\julio\\source\\" + f.filename)
        return 'ok'
