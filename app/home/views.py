
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
    #namespace = jinja2_escapejs_filter("media")
    namespace = "media"
    #field_list = Media.query.all()[0].field_list()
    # field_list = jinja2_escapejs_filter([{'name': 'name', 'type': 'text'}, {'name': 'category', 'type': 'select'}, {'name': 'url', 'type': 'text'}, {'name': 'tags', 'type': 'text'},{'name': 'assigned', 'type': 'select'}])
    # hide = jinja2_escapejs_filter(['timestamp'])

    categorys = Category.query.all()
    mt = []
    for t in categorys:
        data = {"name": t.name, "id": t.id}
        mt.append(data)

    return render_template('home/table.html', title='Database', namespace=namespace, db_filter="fonts", menu=mt)


@home.route('/category', methods=['GET'])
@login_required
def category():
    namespace = jinja2_escapejs_filter("category")
    return render_template('home/table.html', title='Category', namespace=namespace)

@home.route('/user', methods=['GET'])
@login_required
def user():
    namespace = jinja2_escapejs_filter("user")
    return render_template('home/table.html', title='Users', namespace=namespace)


@home.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        base_path = r"C:\\Users\\julio\\source\\"
        f = request.files['file']
        category  = request.args.get('category')
        file_id = request.args.get('file_id')
        file_path = "%s\\%s\\%s\\%s" % (base_path, category, file_id, f.filename)
        print file_path
        #f.save(file_path)
        return 'ok'


# passing data directly to html
@home.route('/test', methods=['GET'])
def test():
    namespace = "media"
    model = getModel(namespace)
    items = model.query.all()
    fields, columns, columnDefs = getFields(model)

    dt_data = []
    for row in items:
        dt_data.append(row.as_dict1(fields))

    dt_data = jinja2_escapejs_filter(dt_data)
    columns = jinja2_escapejs_filter(columns)
    columnDefs = jinja2_escapejs_filter(columnDefs)

    return render_template('home/test.html', title='test', namespace=json.dumps(namespace), data=dt_data, columns=columns, columnDefs=columnDefs)

# standard data_table js ajax call
@home.route('/test_ajax', methods=['GET'])
def test_ajax():
    namespace = "media"
    model = getModel(namespace)
    items = model.query.all()
    fields, columns, columnDefs = getFields(model)

    columns = jinja2_escapejs_filter(columns)
    columnDefs = jinja2_escapejs_filter(columnDefs)

    return render_template('home/test_ajax.html', title='test', namespace=json.dumps(namespace), columns=columns, columnDefs=columnDefs)

@home.route('/test_ajax_socket', methods=['GET'])
def test_ajax_socket():
    namespace = "media"
    model = getModel(namespace)
    items = model.query.all()
    fields, columns, columnDefs = getFields(model)

    columns = jinja2_escapejs_filter(columns)
    columnDefs = jinja2_escapejs_filter(columnDefs)

    return render_template('home/test_ajax_socket.html', title='test', namespace=json.dumps(namespace), columns=columns, columnDefs=columnDefs)


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

@home.route('/ajax_data', methods=['GET'])
def ajax_data():
    namespace = "media"
    model = getModel(namespace)
    items = model.query.all()

    dt_data = []
    for row in items:
        dt_data.append(row.as_dict1(fields))
    t = {"data": dt_data}
    return json.dumps(t)

@home.route('/ajax1', methods=['GET'])
def ajax1():
    request.args
    print request.args.get('draw')
    params = request.args.to_dict()
    print params
    # for k in request.args:
    #     print k
    #q = Mdoel.query.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)

    t = {"draw": 1,"recordsTotal": 57,"recordsFiltered": 57,"data": [
[
      "Gloria",
      "Little",
      "Systems Administrator",
      "New York",
      "10th Apr 09",
      "$237,500"
    ],
    [
      "Haley",
      "Kennedy",
      "Senior Marketing Designer",
      "London",
      "18th Dec 12",
      "$313,500"
    ],
    [
      "Hermione",
      "Butler",
      "Regional Director",
      "London",
      "21st Mar 11",
      "$356,250"
    ],
    [
      "Herrod",
      "Chandler",
      "Sales Assistant",
      "San Francisco",
      "6th Aug 12",
      "$137,500"
    ],
    [
      "Hope",
      "Fuentes",
      "Secretary",
      "San Francisco",
      "12th Feb 10",
      "$109,850"
    ],
    [
      "Howard",
      "Hatfield",
      "Office Manager",
      "San Francisco",
      "16th Dec 08",
      "$164,500"
    ],
    [
      "Jackson",
      "Bradshaw",
      "Director",
      "New York",
      "26th Sep 08",
      "$645,750"
    ],
    [
      "Jena",
      "Gaines",
      "Office Manager",
      "London",
      "19th Dec 08",
      "$90,560"
    ],
    [
      "Jenette",
      "Caldwell",
      "Development Lead",
      "New York",
      "3rd Sep 11",
      "$345,000"
    ],
    [
      "Jennifer",
      "Chang",
      "Regional Director",
      "Singapore",
      "14th Nov 10",
      "$357,650"
    ]
    ]}
    return json.dumps(t)

