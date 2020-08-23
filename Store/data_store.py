import json
import hashlib
import redis
import time


class DataStore:
    def __init__(self, redis_host):
        self.redis_if = redis.Redis(host=redis_host, port=6379, db=2, charset="utf-8", decode_responses=True)
        time.sleep(0.05)
        # Refresh hashes to include stuff added offline
        self.redis_if.set('Applications-hash', self.calc_applications_hash())
        self.redis_if.set('Peripherals-hash', self.calc_peripherals_hash())
        self.redis_if.set('Scripts-hash', self.calc_scripts_hash())
        self.redis_if.set('Programs-hash', self.calc_program_hash())

    # PERIPHERALS

    def load_peripherals(self):
        peripherals = self.redis_if.hgetall('Peripherals')
        for i in peripherals:
            peripherals[i] = json.loads(peripherals[i])
        return peripherals

    def get_peripherals_hash(self):
        return self.redis_if.get('Peripherals-hash')

    def calc_peripherals_hash(self):
        return hashlib.sha256(json.dumps(self.load_peripherals(), sort_keys=True, separators=(',', ':')).encode()).hexdigest()

    def get_peripherals(self):
        return self.load_peripherals()

    def add_peripheral(self, key: str, periph: dict):
        self.redis_if.hset('Peripherals', key, json.dumps(periph))
        hash = self.calc_peripherals_hash()
        self.redis_if.set('Peripherals-hash', hash)

    def remove_peripheral(self, peripheral):
        self.redis_if.hdel('Peripherals', peripheral)
        hash = self.calc_peripherals_hash()
        self.redis_if.set('Peripherals-hash', hash)

    # APPLICATIONS

    def add_application(self, key: str, app: dict):
        self.redis_if.hset('Applications', key, json.dumps(app))
        hash = self.calc_applications_hash()
        self.redis_if.set('Applications-hash', hash)

    def remove_application(self, app):
        self.redis_if.hdel('Applications', app)
        hash = self.calc_applications_hash()
        self.redis_if.set('Applications-hash', hash)

    def load_applications(self):
        applications = self.redis_if.hgetall('Applications')
        for i in applications:
            applications[i] = json.loads(applications[i])
        return applications

    def get_applications(self):
        return self.load_applications()

    def get_applications_hash(self):
        return self.redis_if.get('Applications-hash')

    def calc_applications_hash(self):
        return hashlib.sha256(json.dumps(self.load_applications(), sort_keys=True, separators=(',', ':')).encode()).hexdigest()

    def get_application(self, name):
        app = self.redis_if.hget('Applications', name)
        return json.loads(app)

    # SCRIPTS
    def get_scripts(self):
        scripts = self.redis_if.hgetall('Scripts')
        for i in scripts:
            scripts[i] = json.loads(scripts[i])
        return scripts

    def load_scripts(self):
        scripts = self.redis_if.hgetall('Scripts')
        scripts_list = []
        for i in scripts:
            scripts_list.append(json.loads(scripts[i]))
        return scripts_list

    def add_scripts(self, script_id, script):
        self.redis_if.hset('Scripts', script_id, json.dumps(script))
        hash = self.calc_scripts_hash()
        self.redis_if.set('Scripts-hash', hash)

    def remove_scripts(self, script):
        self.redis_if.hdel('Scripts', script)
        hash = self.calc_applications_hash()
        self.redis_if.set('Scripts-hash', hash)

    def get_scripts_hash(self):
        return self.redis_if.get('Scripts-hash')

    def calc_scripts_hash(self):
        return hashlib.sha256(json.dumps(self.load_scripts(), sort_keys=True, separators=(',', ':')).encode()).hexdigest()

    # PROGRAMS

    def get_programs(self):
        scripts = self.redis_if.hgetall('Programs')
        for i in scripts:
            scripts[i] = json.loads(scripts[i])
        return scripts

    def load_programs(self):
        programs = self.redis_if.hgetall('Programs')
        programs_list = []
        for i in programs:
            programs_list.append(json.loads(programs[i]))
        return programs_list

    def add_program(self, program_id, program):
        self.redis_if.hset('Programs', program_id, json.dumps(program))
        hash = self.calc_scripts_hash()
        self.redis_if.set('Programs-hash', hash)

    def remove_program(self, program):
        self.redis_if.hdel('Programs', program)
        hash = self.calc_applications_hash()
        self.redis_if.set('Programs-hash', hash)

    def get_program_hash(self):
        return self.redis_if.get('Programs-hash')

    def calc_program_hash(self):
        return hashlib.sha256(
            json.dumps(self.load_programs(), sort_keys=True, separators=(',', ':')).encode()).hexdigest()
