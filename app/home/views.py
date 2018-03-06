
from flask import flash, request, redirect, render_template, url_for, json
from flask_login import login_required
import jinja2

from . import home
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

@home.route('/projects', methods=['GET'])    
@login_required
def projects():
    namespace = jinja2_escapejs_filter("project")
    field_list = jinja2_escapejs_filter([{'name': 'name', 'type': 'text'}, {'name': 'status', 'type': 'select'}, {'name': 'assigned', 'type': 'select'}, {'name': 'assets', 'type': 'inline'}])
    hide = jinja2_escapejs_filter(['timestamp'])
    return render_template('home/table.html', title='Projects', namespace=namespace, field_list=field_list, hide=hide)

@home.route('/status', methods=['GET'])
@login_required
def status():
    namespace = jinja2_escapejs_filter("status")
    field_list = jinja2_escapejs_filter([{'name': 'name', 'type': 'text'}])    
    return render_template('home/table.html', title='Status', namespace=namespace, field_list=field_list)

@home.route('/task', methods=['GET'])
@login_required
def task():
    namespace = jinja2_escapejs_filter('task')
    field_list = jinja2_escapejs_filter([{'name': 'name', 'type': 'text'}, {'name': 'parent_key', 'type': 'text'}, {'name': 'process', 'type': 'select'}])
    return render_template('home/table.html', title='Tasks', namespace=namespace, field_list=field_list)

@home.route('/assets', methods=['GET'])
@login_required
def assets():
    namespace = jinja2_escapejs_filter('asset')
    field_list = jinja2_escapejs_filter([{'name': 'name', 'type': 'text'}, {'name': 'project', 'type': 'select'}, {'name': 'process', 'type': 'checkbox'}, {'name': 'asset_type', 'type': 'select'}])
    return render_template('home/table.html', title="Assets", namespace=namespace, field_list=field_list)

@home.route('/asset_type', methods=['GET'])
@login_required
def asset_type():
    namespace = jinja2_escapejs_filter('asset_type')
    field_list = jinja2_escapejs_filter([{'name': 'name', 'type': 'text'}])
    return render_template('home/table.html', title="Asset type", namespace=namespace, field_list=field_list)

@home.route('/shots', methods=['GET'])
@login_required
def shots():
    namespace = jinja2_escapejs_filter('shot')
    field_list = jinja2_escapejs_filter([{'name': 'name', 'type': 'text'}, {'name': 'project', 'type': 'select'}, {'name': 'process', 'type': 'checkbox'}])
    return render_template('home/table.html', title="Shots", namespace=namespace, field_list=field_list)

@home.route('/process', methods=['GET'])
@login_required
def process():
    namespace = jinja2_escapejs_filter('process')
    field_list = jinja2_escapejs_filter([{'name': 'name', 'type': 'text'}, {'name': 'pipeline', 'type': 'select'}])
    return render_template('home/table.html', title="Process", namespace=namespace, field_list=field_list)    

@home.route('/pipeline', methods=['GET'])
@login_required
def pipeline():
    namespace = jinja2_escapejs_filter('pipeline')
    field_list = jinja2_escapejs_filter([{'name': 'name', 'type': 'text'}])
    return render_template('home/table.html', title="Process", namespace=namespace, field_list=field_list)        