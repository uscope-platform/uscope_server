import tarfile
import json


class DataStore:

    def __init__(self, filename):
        tar = tarfile.open(filename, 'r:xz')
        self.applications = json.load(tar.extractfile(tar.getmember('Applications.json')))
        self.peripherals = json.load(tar.extractfile(tar.getmember('Peripherals.json')))
        self.manifest = json.load(tar.extractfile(tar.getmember('manifest.json')))

    def load_applications(self):
        return self.applications

    def load_application(self, name):
        return self.applications[name]

    def load_peripherals(self):
        return self.peripherals

    def load_manifest(self):
        return self.manifest
