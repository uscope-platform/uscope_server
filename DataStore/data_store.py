import tarfile
import json
import os


class DataStore:

    def __init__(self, filename):
        tar = tarfile.open(filename, 'r:xz')
        self.filename = filename
        self.applications = json.load(tar.extractfile(tar.getmember('Applications.json')))
        self.peripherals = json.load(tar.extractfile(tar.getmember('Peripherals.json')))
        self.manifest = json.load(tar.extractfile(tar.getmember('manifest.json')))
        tar.close()

    def load_applications(self):
        return self.applications

    def load_application(self, name):
        return self.applications[name]

    def load_peripherals(self):
        return self.peripherals

    def load_manifest(self):
        return self.manifest

    def add_peripheral(self, periph):
        self.peripherals = {**self.peripherals, **periph}
        with open('Applications.json', 'w') as f:
            json.dump(self.applications, f)
        with open('Peripherals.json', 'w') as f:
            json.dump(self.peripherals, f)
        with open('manifest.json', 'w') as f:
            json.dump(self.manifest, f)

        tar = tarfile.open("uDB", 'w:xz')

        for f in ['Applications.json', 'Peripherals.json', 'manifest.json']:
            tar.add(f)
        tar.close()

        for f in ['Applications.json', 'Peripherals.json', 'manifest.json']:
            os.remove(f)