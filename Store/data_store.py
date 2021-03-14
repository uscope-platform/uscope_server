import json
import hashlib
import redis
import time
import psycopg2
import psycopg2.extras
import uuid
import datetime


def program_from_row(row):
    return {'id': row[0], 'name': row[1], 'path': row[2], 'program_content': row[3], 'program_type': row[4],
                    'hex': row[5]}


def script_from_row(row):
    return {'id': row[0], 'name': row[1], 'path': row[2], 'script_content': row[3], 'triggers': row[4]}


class DataStore:
    def __init__(self, redis_host):
        self.redis_if = redis.Redis(host=redis_host, port=6379, db=2, charset="utf-8", decode_responses=True)
        self.pg_db = psycopg2.connect("dbname=uscope user=uscope password=test host=database")
        self.db = self.pg_db.cursor()
        time.sleep(0.05)
        # Refresh hashes to include stuff added offline
        self.redis_if.set('Applications-hash', self.calc_applications_hash())
        self.redis_if.set('Peripherals-hash', self.calc_peripherals_hash())
        self.update_version('scripts')
        self.update_version('programs')

    def __del__(self):
        self.pg_db.close()

    def get_version(self, table):
        self.db.execute('SELECT version FROM uscope.data_versions WHERE "table" LIKE (%s)', (table,))
        self.pg_db.commit()
        return str(self.db.fetchone()[0])

    def update_version(self, table):
        uid = uuid.uuid4()
        time = datetime.datetime.now()
        row_data = (table, uid, time)
        psycopg2.extras.register_uuid()
        self.db.execute("""INSERT INTO uscope.data_versions ("table", version, last_modified) VALUES (%s,%s, %s)
                                   ON CONFLICT ("table") DO UPDATE 
                                       SET version = excluded.version, 
                                           last_modified = excluded.last_modified""", row_data)
        self.pg_db.commit()

    # PERIPHERALS

    def load_peripherals(self):
        peripherals = self.redis_if.hgetall('Peripherals')
        for i in peripherals:
            peripherals[i] = json.loads(peripherals[i])
        return peripherals

    def get_peripherals_hash(self):
        return self.redis_if.get('Peripherals-hash')

    def calc_peripherals_hash(self):
        return hashlib.sha256(
            json.dumps(self.load_peripherals(), sort_keys=True, separators=(',', ':')).encode()).hexdigest()

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
        return hashlib.sha256(
            json.dumps(self.load_applications(), sort_keys=True, separators=(',', ':')).encode()).hexdigest()

    def get_application(self, name):
        app = self.redis_if.hget('Applications', name)
        return json.loads(app)

    # SCRIPTS

    def get_script(self, id):
        self.db.execute("SELECT * FROM uscope.scripts WHERE id = %s", (id,))
        self.pg_db.commit()
        return script_from_row(self.db.fetchone())

    def get_scripts_dict(self):
        self.db.execute("SELECT * FROM  uscope.scripts")
        self.pg_db.commit()

        scripts = {}
        for row in self.db.fetchall():
            scripts[row[0]] = script_from_row(row)

        return scripts

    def add_scripts(self, script_id, script):
        row_data = (script_id, script['name'], script['path'], script['script_content'], script['triggers'])
        self.db.execute("""INSERT INTO uscope.scripts (id, name, path, content, triggers) VALUES (%s,%s,%s,%s,%s)
                                   ON CONFLICT (id) DO UPDATE
                                       SET name = excluded.name,
                                           path = excluded.path,
                                           content = excluded.content,
                                           triggers = excluded.triggers;
                                    """,
                        row_data)
        self.pg_db.commit()

        self.update_version('scripts')

    def remove_scripts(self, script):
        row_data = (script,)
        self.db.execute("DELETE FROM uscope.scripts WHERE id = %s", row_data)
        self.update_version('scripts')

    def get_scripts_hash(self):
        return self.get_version('scripts')

    # PROGRAMS

    def get_program(self, id):
        self.db.execute("SELECT * FROM uscope.programs WHERE id = %s", (id,))
        self.pg_db.commit()
        return program_from_row(self.db.fetchone())

    def get_programs_dict(self):
        self.db.execute("SELECT * FROM uscope.programs")
        self.pg_db.commit()

        pg_programs = {}
        for row in self.db.fetchall():
            pg_programs[row[0]] = program_from_row(row)

        return pg_programs

    def add_program(self, program_id, program):
        if 'hex' in program:
            hex_val = program['hex']
        else:
            hex_val = []
        row_data = (program_id, program['name'], program['path'], program['program_content'], program['program_type'],
                    hex_val)
        self.db.execute("""INSERT INTO uscope.programs (id, name, path, content, type, hex) VALUES (%s,%s,%s,%s,%s,%s) 
                           ON CONFLICT (id) DO UPDATE 
                               SET name = excluded.name, 
                                   path = excluded.path,
                                   content = excluded.content,
                                   type = excluded.type,
                                   hex = excluded.hex;
                            """,
                        row_data)
        self.pg_db.commit()

        self.update_version('programs')

    def remove_program(self, program):
        row_data = (program,)
        self.db.execute("DELETE FROM uscope.programs WHERE id = %s", row_data)
        self.pg_db.commit()

        self.update_version('programs')

    def get_program_hash(self):
        return self.get_version('programs')
