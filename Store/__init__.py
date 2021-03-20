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
        self.Auth.restore(data['auth'])
        self.Settings.restore(data['settings'])
        self.Elements.restore(data['elements'])
