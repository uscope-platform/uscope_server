import json
import hashlib
import redis


class DataStore:
    def __init__(self, redis_host):
        self.redis_if = redis.Redis(host=redis_host, port=6379, db=2, charset="utf-8", decode_responses=True)

    def load_applications(self):
        applications = self.redis_if.hgetall('Applications')
        for i in applications:
            applications[i] = json.loads(applications[i])
        return applications

    def load_peripherals(self):
        peripherals = self.redis_if.hgetall('Peripherals')
        for i in peripherals:
            peripherals[i] = json.loads(peripherals[i])
        return peripherals

    def get_applications(self):
        return self.load_applications()

    def get_applications_hash(self):
        return self.redis_if.get('Applications-hash')

    def calc_applications_hash(self):
        return hashlib.sha256(json.dumps(self.load_applications(), sort_keys=True, separators=(',', ':')).encode()).hexdigest()

    def get_application(self, name):
        app = self.redis_if.hget('Applications', name)
        return json.loads(app)

    def get_peripherals_hash(self):
        return self.redis_if.get('Peripherals-hash')

    def calc_peripherals_hash(self):
        return hashlib.sha256(json.dumps(self.load_peripherals(), sort_keys=True, separators=(',', ':')).encode()).hexdigest()

    def get_peripherals(self):
        return self.load_peripherals()

    def add_peripheral(self, periph: dict):
        key, value = periph.popitem()
        self.redis_if.hset('Peripherals', key, json.dumps(value))
        hash = self.calc_peripherals_hash()
        self.redis_if.set('Peripherals-hash', hash)

    def remove_peripheral(self, peripheral):
        self.redis_if.hdel('Peripherals', peripheral)
        hash = self.calc_peripherals_hash()
        self.redis_if.set('Peripherals-hash', hash)

    def add_application(self, app):
        key, value = app.popitem()
        self.redis_if.hset('Applications', key, json.dumps(value))
        hash = self.calc_applications_hash()
        self.redis_if.set('Applications-hash', hash)

    def remove_application(self, app):
        self.redis_if.hdel('Applications', app)
        hash = self.calc_applications_hash()
        self.redis_if.set('Applications-hash', hash)
