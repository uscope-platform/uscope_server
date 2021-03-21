from .ElementDataStore import ElementsDataStore
from .AuthStore import AuthStore
from .SettingsStore import SettingsStore


class Store:
    def __init__(self):
        self.Auth = AuthStore()
        self.Settings = SettingsStore()
        self.Elements = ElementsDataStore()

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
