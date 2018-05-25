# https://flask-migrate.readthedocs.io/en/latest/

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import flask_whooshalchemy
from flask_socketio import SocketIO, emit
#from whoosh.analysis import IDTokenizer

from config import app_config

#base_path = "C:/Users/julio/Dropbox/Projects/mcd_database/assets"
base_path = r"/mnt/assets"

db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO()

def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config['development'])
    app.config.from_pyfile(config_name)
    #app.config['WHOOSH_ANALYZER'] = IDTokenizer()
    from models import Media
    flask_whooshalchemy.whoosh_index(app, Media)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_message = "You must login!" 
    login_manager.login_view = "auth.login" # redirect to here

    migrate = Migrate(app, db)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .home import home as home_blueprint
    app.register_blueprint(home_blueprint)    

    socketio.init_app(app)
    return app