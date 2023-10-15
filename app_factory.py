# Copyright 2021 University of Nottingham Ningbo China
# Author: Filippo Savi <filssavi@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

import logging
import os

from uCube_interface import uCube_interface
from Store import Store, MockStore


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


def create_app():
    driver_host = os.environ.get('DRIVER_HOST')

    app = Flask(__name__)
    app.config.from_object("server_config")

    jwt = JWTManager(app)

    if os.environ.get("DEBUG") == "TRUE":
        CORS(app)

    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger("sqlitedict").setLevel(logging.WARNING)


    app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix='/uscope')

    interface = uCube_interface.uCube_interface(driver_host, 6666)

    if os.environ.get("TESTING") == "TRUE":
        store = MockStore()
    else:
        store = Store()

    app.store = store

    with app.app_context():
        # Include our Routes
        from uScopeBackend.application_manager import application_manager_bp, ApplicationManager
        from uScopeBackend.plot_manager import plot_manager_bp, PlotManager
        from uScopeBackend.registers_manager import registers_manager_bp, RegistersManager
        from uScopeBackend.peripheral_manager import peripheral_manager_bp, PeripheralManager
        from uScopeBackend.scripts_manager import scripts_manager_bp, ScriptManager
        from uScopeBackend.programs_manager import programs_manager_bp, ProgramsManager
        from uScopeBackend.db_manager import database_manager_bp, DatabaseManager
        from uScopeBackend.auth_manager import auth_manager_bp, AuthManager
        from uScopeBackend.bitstream_manager import bitstream_manager_bp, BitstreamManager
        from uScopeBackend.filters_manager import filters_manager_bp, FilterManager
        from uScopeBackend.emulator_manager import emulator_manager_bp, EmulatorManager

        app.interface = interface

        app.app_mgr = ApplicationManager(interface, store)
        app.plot_mgr = PlotManager(interface, store)
        app.register_mgr = RegistersManager(interface, store)
        app.programs_mgr = ProgramsManager(interface, store)
        app.peripheral_mgr = PeripheralManager(store)
        app.script_mgr = ScriptManager(store)
        app.db_mgr = DatabaseManager(store, interface)
        app.auth_mgr = AuthManager(store)
        app.bitstream_mgr = BitstreamManager(store)
        app.filter_mgr = FilterManager(store)
        app.emu_mgr = EmulatorManager(store)

        # Register Blueprints
        app.register_blueprint(application_manager_bp)
        app.register_blueprint(plot_manager_bp)
        app.register_blueprint(peripheral_manager_bp)
        app.register_blueprint(registers_manager_bp)
        app.register_blueprint(programs_manager_bp)
        app.register_blueprint(scripts_manager_bp)
        app.register_blueprint(database_manager_bp)
        app.register_blueprint(auth_manager_bp)
        app.register_blueprint(bitstream_manager_bp)
        app.register_blueprint(filters_manager_bp)
        app.register_blueprint(emulator_manager_bp)

    return app
