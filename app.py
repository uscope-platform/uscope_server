from flask import Flask
import logging
import sys

from uCube_interface import uCube_interface

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uScope-CORS-key'
app.config['CORS_HEADERS'] = 'Content-Type'

log = logging.getLogger('werkzeug')

log.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':

    if len(sys.argv) > 1 and sys.argv[1] == "DBG":
        interface = uCube_interface.uCube_interface(dbg=True)
    else:
        interface = uCube_interface.uCube_interface(dbg=False)

    with app.app_context():

        # Include our Routes
        from uScopeBackend.application_manager import application_manager_bp, ApplicationManager
        from uScopeBackend.plot_manager import plot_manager_bp, PlotManager
        from uScopeBackend.registers_manager import registers_manager_bp, RegistersManager

        app.app_mgr = ApplicationManager(interface)
        app.plot_mgr = PlotManager(interface)
        app.register_mgr = RegistersManager(interface)

        # Register Blueprints
        app.register_blueprint(application_manager_bp)
        app.register_blueprint(plot_manager_bp)
        app.register_blueprint(registers_manager_bp)

    app.run(host='0.0.0.0', threaded=True, port=5000)
