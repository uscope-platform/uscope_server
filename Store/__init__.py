from .ElementDataStore import ElementsDataStore
from .AuthStore import AuthStore
from .SettingsStore import SettingsStore
from sqlalchemy.exc import OperationalError
import os
import time


class Store:
    def __init__(self, clear_settings=True, update_ude_versions_on_init=True):

        debug_config = os.environ.get("DEBUG")
        if debug_config == "TRUE":
            redis_host="localhost"
            pg_host="postgresql+psycopg2://uscope:test@localhost/uscope"
        else:
            redis_host="redis"
            pg_host="postgresql+psycopg2://uscope:test@database/uscope"

        self.Settings = SettingsStore(clear_settings=clear_settings, host=redis_host)

        pg_available = False
        pg_start_tries_left = 300
        while not pg_available:
            try:
                self.Auth = AuthStore(pg_host)
                self.Elements = ElementsDataStore(update_ude_versions_on_init=update_ude_versions_on_init,host=pg_host)
            except OperationalError:
                if pg_start_tries_left == 0:
                    raise RuntimeError("ERROR: Could not connect to the postgres database")
                pg_start_tries_left -= 1
                time.sleep(0.8)
            else:
                pg_available = True

    def dump(self):
        dump = {'auth': self.Auth.dump(), 'elements': self.Elements.dump(), 'settings': self.Settings.dump()}
        return dump

    def restore(self, data):
        print("restoring Users")
        self.Auth.restore(data['auth'])
        print("restoring Elements")
        self.Elements.restore(data['elements'])
        print("restoring settings")
        self.Settings.restore(data['settings'])
