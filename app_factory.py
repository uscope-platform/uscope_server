from flask import Flask
from flask_cors import CORS

import logging
import os

from uCube_interface import uCube_interface
from uCube_interface import emulated_interface
from Store.data_store import DataStore
from Store.auth_store import AuthStore
from flask_jwt_extended import JWTManager

class PrefixMiddleware(object):

    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):

        if environ['PATH_INFO'].startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)
        else:
            start_response('404', [('Content-Type', 'text/plain')])
            return ["This url does not belong to the app.".encode()]



def create_app(debug=False):

    app = Flask(__name__, instance_relative_config=True)
    app.config['SECRET_KEY'] = 'uScope-CORS-key'
    app.config['CORS_HEADERS'] = 'Content-Type'
    app.config['JWT_SECRET_KEY'] = 'uScope-JWT-key'  # Change this!
    jwt = JWTManager(app)
    CORS(app)

    logging.getLogger('werkzeug').setLevel(logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("sqlitedict").setLevel(logging.CRITICAL)

    if debug:
        app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix='/uscope')
        redis_host = 'localhost'
        interface = emulated_interface.EmulatedInterface()
    else:
        redis_host = 'localhost'
        interface = uCube_interface.uCube_interface(redis_host)

    data_store = DataStore(redis_host)
    auth_store = AuthStore(redis_host)

    with app.app_context():

        # Include our Routes
        from uScopeBackend.application_manager import application_manager_bp, ApplicationManager
        from uScopeBackend.plot_manager import plot_manager_bp, PlotManager
        from uScopeBackend.registers_manager import registers_manager_bp, RegistersManager
        from uScopeBackend.tab_creator_manager import tab_creator_manager_bp,TabCreatorManager
        from uScopeBackend.scripts_manager import scripts_manager_bp, ScriptManager
        from uScopeBackend.db_manager import database_manager_bp, DatabaseManager
        from uScopeBackend.auth_manager import auth_manager_bp, AuthManager

        app.interface = interface
        app.app_mgr = ApplicationManager(interface, data_store, redis_host)
        app.plot_mgr = PlotManager(interface, data_store, redis_host)
        app.register_mgr = RegistersManager(interface, data_store)
        app.tab_creator_mgr = TabCreatorManager(data_store)
        app.script_mgr = ScriptManager(data_store)
        app.db_mgr = DatabaseManager('/var/lib/redis/6379/dump.rdb')
        app.auth_mgr = AuthManager(auth_store)

        # Register Blueprints
        app.register_blueprint(application_manager_bp)
        app.register_blueprint(plot_manager_bp)
        app.register_blueprint(tab_creator_manager_bp)
        app.register_blueprint(registers_manager_bp)
        app.register_blueprint(scripts_manager_bp)
        app.register_blueprint(database_manager_bp)
        app.register_blueprint(auth_manager_bp)
    return app