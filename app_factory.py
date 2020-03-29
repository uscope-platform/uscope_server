from flask import Flask
from flask_cors import CORS

import logging
import os

from uCube_interface import uCube_interface
from DataStore.data_store import DataStore


def create_app(debug=False):

    app = Flask(__name__, instance_relative_config=True)
    app.config['SECRET_KEY'] = 'uScope-CORS-key'
    app.config['CORS_HEADERS'] = 'Content-Type'
    CORS(app)

    logging.getLogger('werkzeug').setLevel(logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("sqlitedict").setLevel(logging.CRITICAL)

    if debug:
        redis_host = 'localhost'
        interface = uCube_interface.uCube_interface(redis_host)
    else:
        redis_host = 'localhost'
        interface = uCube_interface.uCube_interface(redis_host)

    store = DataStore(redis_host)

    with app.app_context():

        # Include our Routes
        from uScopeBackend.application_manager import application_manager_bp, ApplicationManager
        from uScopeBackend.plot_manager import plot_manager_bp, PlotManager
        from uScopeBackend.registers_manager import registers_manager_bp, RegistersManager
        from uScopeBackend.tab_creator_manager import tab_creator_manager_bp,TabCreatorManager
        from uScopeBackend.scripts_manager import scripts__manager_bp, ScriptManager
        from uScopeBackend.db_manager import database__manager_bp, DatabaseManager

        app.app_mgr = ApplicationManager(interface, store, redis_host)
        app.plot_mgr = PlotManager(interface, store, redis_host)
        app.register_mgr = RegistersManager(interface, store)
        app.tab_creator_mgr = TabCreatorManager(store)
        app.script_mgr = ScriptManager(store)
        app.db_mgr = DatabaseManager('/var/lib/redis/6379/dump.rdb')

        # Register Blueprints
        app.register_blueprint(application_manager_bp)
        app.register_blueprint(plot_manager_bp)
        app.register_blueprint(tab_creator_manager_bp)
        app.register_blueprint(registers_manager_bp)
        app.register_blueprint(scripts__manager_bp)
        app.register_blueprint(database__manager_bp)
    return app