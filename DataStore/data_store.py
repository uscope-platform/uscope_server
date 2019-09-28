import tarfile
import json
import os
import hashlib
from threading import Lock
from flask import jsonify

class DataStore:

    def __init__(self, filename):
        json.encoder.FLOAT_REPR = lambda x: format(x, '.12f')
        self.database_lock = Lock()
        tar = tarfile.open(filename, 'r:xz')
        self.filename = filename
        self.applications = json.load(tar.extractfile(tar.getmember('Applications.json')))
        self.peripherals = json.load(tar.extractfile(tar.getmember('Peripherals.json')))
        self.manifest = json.load(tar.extractfile(tar.getmember('manifest.json')))
        tar.close()

    def get_applications(self):
        return self.applications

    def get_applications_hash(self):
        return hashlib.sha256(json.dumps(self.applications, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

    def get_application(self, name):
        return self.applications[name]

    def get_peripherals_hash(self):
        return hashlib.sha256(json.dumps(self.peripherals, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

    def get_peripherals(self):
        return self.peripherals

    def get_manifest_hash(self):
        return hashlib.sha256(json.dumps(self.manifest, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

    def get_manifest(self):
        return self.manifest

    def __persist_udb(self):
        self.database_lock.acquire()
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
        self.database_lock.release()

    def add_peripheral(self, periph):
        self.peripherals = {**self.peripherals, **periph}
        self.__persist_udb()

    def remove_peripheral(self, peripheral):
        del self.peripherals[peripheral]
        self.__persist_udb()
