
from sqlalchemy.orm import declarative_base, sessionmaker

from sqlalchemy import create_engine

import Applications
import Scripts

# declarative base class
Base = declarative_base()


class DataStore:

    def __init__(self):
        self.engine = create_engine("postgresql+psycopg2://uscope:test@172.23.0.4/uscope")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        self.app_store = Applications.ApplicationsStore(self.Session)
        self.script_store = Scripts.ScriptsStore(self.Session)

    def add_application(self, app):
        self.app_store.add_application(app)

    def get_applications_dict(self):
        return self.app_store.get_applications_dict()

    def get_application(self, name):
        return self.app_store.get_application(name)

    def remove_application(self, name):
        self.app_store.remove_application(name)

    def get_script(self, id):
        return self.script_store.get_script(id)

    def get_scripts_dict(self):
        return self.script_store.get_scripts_dict()

    def add_scripts(self, script):
        self.script_store.add_scripts(script)

    def remove_scripts(self, script):
        self.script_store.remove_scripts(script)


store = DataStore()

result = store.get_applications_dict()
result1 = store.get_application('SicDrive')

app = {'application_name': "test", 'bitstream': "test.bin", 'clock_frequency': 10000, 'channels': [],
       'channel_groups': [], 'initial_registers_values': [], 'macro': [], 'parameters': [], 'peripherals': []}

store.add_application(app)
store.remove_application("test")

scripts = store.get_scripts_dict()
script = store.get_script(25)

scr = {'id': 100, 'name': "test", 'path': 'test.sh', 'script_content': 'asfgfweg', 'triggers': 'test trigger'}
store.add_scripts(scr)
store.remove_scripts(100)
pass