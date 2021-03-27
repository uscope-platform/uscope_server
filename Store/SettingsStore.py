from sqlalchemy.orm import declarative_base, sessionmaker

from sqlalchemy import create_engine
from .Elements import Settings


class SettingsStore:
    def __init__(self, host=None, clear_settings=True):
        if host:
            self.engine = create_engine("postgresql+psycopg2://uscope:test@" + host + "/uscope")
        else:
            self.engine = create_engine("postgresql+psycopg2://uscope:test@database/uscope")

        Base = declarative_base()
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.settings_db = Settings.SettingsDatabase(self.Session)
        if clear_settings:
            self.clear_settings()

    def get_value(self, name, username):
        if not username:
            raise RuntimeError("The username is needed to retrive a setting")
        return self.settings_db.get_value(name, username)

    def set_value(self, name, value, username):
        if not username:
            raise RuntimeError("The username is needed to store a setting")
        self.settings_db.set_value(name, value, username)

    def clear_settings(self):
        print("CLEARED SETTINGS")
        self.settings_db.clear_settings()

    def dump(self):
        return self.settings_db.dump()

    def restore(self, data):
        self.settings_db.restore(data)