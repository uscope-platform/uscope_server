from .ElementDataStore import ElementsDataStore
from .AuthStore import AuthStore
from .SettingsStore import SettingsStore


class Store:
    def __init__(self, clear_settings=True, update_ude_versions_on_init=True, host=None):
        self.Auth = AuthStore(host)
        if host:
            self.Settings = SettingsStore(clear_settings=clear_settings,host=host)
        else:
            self.Settings = SettingsStore(clear_settings=clear_settings)

        self.Elements = ElementsDataStore(update_ude_versions_on_init=update_ude_versions_on_init,host=host)

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
