"""
This function is the application factory, any configuration, registration, 
and other setup the application needs will happen inside the function, 
then the application will be returned.
"""

import os

__version__ = "0.0.1"

from flask import Flask
from dotenv import load_dotenv
load_dotenv()
UPLOAD_FOLDER = "/tmp"


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, # name of the current Python module
                template_folder="templates", # where html files are stored.  
                static_folder="static", # used for css and js files.              
                instance_relative_config=True
                ) # create flask instance
    app.config.from_mapping(
        SECRET_KEY='dev', # used by Flask and extensions to keep data safe
            # change this to random string when deploying.
        DATABASE=os.path.join(app.instance_path, 'biosimdb.sqlite'), # path 
            # where the SQLite database file will be saved
        MYSQL_CURSORCLASS="DictCursor",
        UPLOAD_FOLDER=UPLOAD_FOLDER,
        DATA_FOLDER=os.path.join(app.instance_path, 'simulations'),
    ) # sets some default configuration that the app will use

    # invenio app configs
    app.config.from_mapping(
        CLIENT_ID = os.getenv("CLIENT_ID", ""),
        CLIENT_SECRET = os.getenv("CLIENT_SECRET", ""),
        AUTH_URL = os.getenv("AUTH_URL"),
        TOKEN_URL= os.getenv("TOKEN_URL"),
        API_BASE = os.getenv("API_BASE"),
        REDIRECT_URI = os.getenv("REDIRECT_URI"),
        SCOPES = os.getenv("SCOPES", "").strip(),
        STATE_FIXED = "xyz123"  # fine for testing; random per-session in prod
    ) # invenio app configs

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # register init-db with the app and be called using the flask command
    # We can run the init-db command to initialize the database with:
    # $ flask --app biosimdb_app init-db
    from .utils import db
    db.init_app(app)

    from .main import bp as main_bp
    app.register_blueprint(main_bp)

    from .data import bp as data_bp
    app.register_blueprint(data_bp)

    from .form import form_bp
    app.register_blueprint(form_bp)

    from .login import bp as login_bp
    app.register_blueprint(login_bp)

    from .invenio import invenio_bp
    app.register_blueprint(invenio_bp)

    return app