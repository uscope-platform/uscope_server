import tarfile
import json
import os
import hashlib
from threading import Lock
from flask import jsonify
import redis


class DataStore:
    def __init__(self, filename,redis_host, backend="udb"):

        self.backend = backend
        if backend is "redis":
            self.redis_if = redis.Redis(host=redis_host, port=6379, db=2, charset="utf-8", decode_responses=True)

            self.load_applications()
            self.load_peripherals()

        elif backend is "udb":
            json.encoder.FLOAT_REPR = lambda x: format(x, '.12f')
            self.database_lock = Lock()
            tar = tarfile.open(filename, 'r:xz')
            self.filename = filename
            self.applications = json.load(tar.extractfile(tar.getmember('Applications.json')))
            self.peripherals = json.load(tar.extractfile(tar.getmember('Peripherals.json')))
            self.manifest = json.load(tar.extractfile(tar.getmember('manifest.json')))
            tar.close()


    def load_applications(self):
        self.applications = self.redis_if.hgetall('Applications')
        for i in self.applications:
            self.applications[i] = json.loads(self.applications[i])

    def load_peripherals(self):
        self.peripherals = self.redis_if.hgetall('Peripherals')
        for i in self.peripherals:
            self.peripherals[i] = json.loads(self.peripherals[i])

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

    def add_peripheral(self, periph: dict):
        self.peripherals = {**self.peripherals, **periph}

        if self.backend is "redis":
            key, value = periph.popitem()
            self.redis_if.hset('Peripherals', key, json.dumps(value))
        elif self.backend is "udb":
            self.__persist_udb()

    def remove_peripheral(self, peripheral):
        del self.peripherals[peripheral]

        if self.backend is "redis":
            self.redis_if.hdel('Peripherals', peripheral)
        elif self.backend is "udb":
            self.__persist_udb()

    def add_application(self, app):
        self.applications = {**self.applications, **app}

        if self.backend is "redis":
            key, value = app.popitem()
            self.redis_if.hset('Applications', key, json.dumps(value))
        elif self.backend is "udb":
            self.__persist_udb()

    def remove_application(self, app):
        del self.applications[app]

        if self.backend is "redis":
            self.redis_if.hdel('Applications', app)
        elif self.backend is "udb":
            self.__persist_udb()
