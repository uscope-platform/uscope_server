from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

import logging
import toml
import os

from uCube_interface import uCube_interface
from Store import Store


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


def create_app(debug=True):
    if os.environ.get('USCOPE_DEPLOYMENT_OPTION') == 'DOCKER':
        driver_host = 'driver'
    else:
        driver_host = '0.0.0.0'

    app = Flask(__name__)
    app.config.from_file("flask.cfg", load=toml.load)

    jwt = JWTManager(app)

    if(debug):
        CORS(app)

    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger("sqlitedict").setLevel(logging.WARNING)

    if debug:
        app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix='/uscope')

    interface = uCube_interface.uCube_interface(driver_host, 6666)

    store = Store()

    with app.app_context():
        # Include our Routes
        from uScopeBackend.application_manager import application_manager_bp, ApplicationManager
        from uScopeBackend.plot_manager import plot_manager_bp, PlotManager
        from uScopeBackend.registers_manager import registers_manager_bp, RegistersManager
        from uScopeBackend.tab_creator_manager import tab_creator_manager_bp,TabCreatorManager
        from uScopeBackend.scripts_manager import scripts_manager_bp, ScriptManager
        from uScopeBackend.programs_manager import programs_manager_bp, ProgramsManager
        from uScopeBackend.db_manager import database_manager_bp, DatabaseManager
        from uScopeBackend.auth_manager import auth_manager_bp, AuthManager
        from uScopeBackend.bitstream_manager import bitstream_manager_bp, BitstreamManager

        app.interface = interface

        app.app_mgr = ApplicationManager(interface, store)
        app.plot_mgr = PlotManager(interface, store, debug)
        app.register_mgr = RegistersManager(interface, store)
        app.programs_mgr = ProgramsManager(interface, store)
        app.tab_creator_mgr = TabCreatorManager(store)
        app.script_mgr = ScriptManager(store)
        app.db_mgr = DatabaseManager(store)
        app.auth_mgr = AuthManager(store)
        app.bitstream_mgr = BitstreamManager(store, debug)

        # Register Blueprints
        app.register_blueprint(application_manager_bp)
        app.register_blueprint(plot_manager_bp)
        app.register_blueprint(tab_creator_manager_bp)
        app.register_blueprint(registers_manager_bp)
        app.register_blueprint(programs_manager_bp)
        app.register_blueprint(scripts_manager_bp)
        app.register_blueprint(database_manager_bp)
        app.register_blueprint(auth_manager_bp)
        app.register_blueprint(bitstream_manager_bp)

    return app
