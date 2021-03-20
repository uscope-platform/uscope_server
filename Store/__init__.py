from .ElementDataStore import ElementsDataStore
from .AuthStore import AuthStore
from .SettingsStore import SettingsStore


class Store:
    def __init__(self):
        self.Auth = AuthStore()
        self.Settings = SettingsStore()
        self.Elements = ElementsDataStore()