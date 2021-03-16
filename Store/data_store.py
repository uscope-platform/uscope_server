import time
import psycopg2
import psycopg2.extras
import uuid
import datetime
import copy

from sqlalchemy import create_engine, text


def program_from_row(row):
    return {'id': row[0], 'name': row[1], 'path': row[2], 'program_content': row[3], 'program_type': row[4],
            'hex': row[5]}


def script_from_row(row):
    return {'id': row[0], 'name': row[1], 'path': row[2], 'script_content': row[3], 'triggers': row[4]}


def application_from_row(row):
    app = {}
    app['application_name'] = row[0]
    app['bitstream'] = row[1]
    app['clock_frequency'] = row[2]
    app['channels'] = row[3]
    app['peripherals'] = row[4]
    app['parameters'] = row[5]
    app['initial_registers_values'] = row[6]
    app['macro'] = row[7]
    app['channel_groups'] = row[8]
    for i in row[9]:
        app[i] = row[9][i]
    return app


def peripheral_from_row(row):
    return {'peripheral_name': row[0], 'image': row[1], 'version': row[2], 'registers': row[3]}


class DataStore:
    def __init__(self):

        self.db_engine = create_engine("postgresql+psycopg2://uscope:test@database/uscope")
        time.sleep(0.05)

        # Refresh hashes to include stuff added offline
        self.update_version('Applications')
        self.update_version('Peripherals')
        self.update_version('scripts')
        self.update_version('programs')

    def get_resource_dict(self, query, constructor_func):
        apps = {}
        with self.db_engine.connect() as connection:
            result = connection.execute(text(query))
            for row in result:
                apps[row[0]] = constructor_func(row)
        return apps

    def run_select_one(self, query, data):
        with self.db_engine.connect() as connection:
            result = connection.execute(query, data)
            result = result.fetchone()
        return result

    def run_query(self, query, data):
        with self.db_engine.connect() as connection:
             connection.execute(query, data)

    def get_version(self, table):
        res = self.run_select_one('SELECT version FROM uscope.data_versions WHERE "table" LIKE (%s)', (table,))
        return str(res[0])

    def update_version(self, table):
        uid = uuid.uuid4()
        time = datetime.datetime.now()
        row_data = (table, uid, time)
        psycopg2.extras.register_uuid()
        self.run_query("""INSERT INTO uscope.data_versions ("table", version, last_modified) VALUES (%s,%s, %s)
                                   ON CONFLICT ("table") DO UPDATE 
                                       SET version = excluded.version, 
                                           last_modified = excluded.last_modified""", row_data)

    # PERIPHERALS

    def get_peripherals_hash(self):
        return self.get_version('Peripherals')

    def get_peripherals_dict(self):
        peripherals = self.get_resource_dict("SELECT * FROM uscope.peripherals", peripheral_from_row)
        return peripherals

    def add_peripheral(self, key: str, periph: dict):

        row_data = (periph['peripheral_name'], periph['image'], periph['version'], psycopg2.extras.Json(periph['registers']))

        self.run_query("""INSERT INTO uscope.peripherals (name, image, version, registers) VALUES (%s,%s,%s,%s)
                                                           ON CONFLICT (name) DO UPDATE
                                                               SET name = excluded.name,
                                                                   image = excluded.image,
                                                                   version = excluded.version,
                                                                   registers = excluded.registers; 
                                                            """,
                       row_data)
        self.update_version('Peripherals')

    def remove_peripheral(self, peripheral):
        self.run_query("DELETE FROM uscope.peripherals WHERE name LIKE %s", (peripheral,))
        self.update_version('Peripherals')

    def get_peripheral(self, peripheral):
        row = self.run_select_one("SELECT * FROM uscope.peripherals WHERE name LIKE %s", (peripheral,))
        return peripheral_from_row(row)

    # APPLICATIONS

    def add_application(self, key: str, app: dict):

        miscellaneous = copy.copy(app)

        standard_items = ('application_name', 'bitstream', 'clock_frequency', 'channels', 'channel_groups',
                          'initial_registers_values', 'macro', 'parameters', 'peripherals')
        for k in standard_items:
            miscellaneous.pop(k, None)

        row_data = (app['application_name'], app['bitstream'], app['clock_frequency'],
                    psycopg2.extras.Json(app['channels']), psycopg2.extras.Json(app['channel_groups']),
                    psycopg2.extras.Json(app['initial_registers_values']), psycopg2.extras.Json(app['macro']),
                    psycopg2.extras.Json(app['parameters']), psycopg2.extras.Json(app['peripherals']),
                    psycopg2.extras.Json(miscellaneous))

        self.run_query("""INSERT INTO uscope.applications (application_name, bitstream, clock_frequency, channels,
                                   channel_groups, initial_registers_values, macro, parameters, peripherals, miscellaneous) 
                                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                                                   ON CONFLICT (application_name) DO UPDATE
                                                       SET application_name = excluded.application_name,
                                                           bitstream = excluded.bitstream,
                                                           clock_frequency = excluded.clock_frequency,
                                                           channels = excluded.channels,
                                                           channel_groups = excluded.channel_groups,
                                                           initial_registers_values = excluded.initial_registers_values,
                                                           macro = excluded.macro,
                                                           parameters = excluded.parameters,
                                                           peripherals = excluded.peripherals,
                                                           miscellaneous = excluded.miscellaneous; 
                                                    """,
                       row_data)

        self.update_version('Applications')

    def remove_application(self, app):
        self.run_query("DELETE FROM uscope.applications WHERE application_name LIKE %s", (app,))
        self.update_version('Applications')

    def get_application(self, app):
        row = self.run_select_one("SELECT * FROM uscope.applications WHERE application_name LIKE %s", (app,))

        return application_from_row(row)

    def get_applications_dict(self):
        res = self.get_resource_dict("SELECT * FROM uscope.applications", application_from_row)
        return res

    def get_applications_hash(self):
        return self.get_version('Applications')

    # SCRIPTS

    def get_script(self, id):
        res = self.run_select_one("SELECT * FROM uscope.scripts WHERE id = %s", (id,))
        return script_from_row(res)

    def get_scripts_dict(self):
        res = self.get_resource_dict("SELECT * FROM  uscope.scripts", script_from_row)
        return res

    def add_scripts(self, script_id, script):
        row_data = (script_id, script['name'], script['path'], script['script_content'], script['triggers'])
        self.run_query("""INSERT INTO uscope.scripts (id, name, path, content, triggers) VALUES (%s,%s,%s,%s,%s)
                                   ON CONFLICT (id) DO UPDATE
                                       SET name = excluded.name,
                                           path = excluded.path,
                                           content = excluded.content,
                                           triggers = excluded.triggers;
                                    """,
                        row_data)

        self.update_version('scripts')

    def remove_scripts(self, script):
        row_data = (script,)
        self.run_query("DELETE FROM uscope.scripts WHERE id = %s", row_data)
        self.update_version('scripts')

    def get_scripts_hash(self):
        return self.get_version('scripts')

    # PROGRAMS

    def get_program(self, id):
        res = self.run_select_one("SELECT * FROM uscope.programs WHERE id = %s", (id,))
        return program_from_row(res)

    def get_programs_dict(self):
        res = self.get_resource_dict("SELECT * FROM uscope.programs", program_from_row)
        return res

    def add_program(self, program_id, program):
        if 'hex' in program:
            hex_val = program['hex']
        else:
            hex_val = []
        row_data = (program_id, program['name'], program['path'], program['program_content'], program['program_type'],
                    hex_val)
        self.run_query("""INSERT INTO uscope.programs (id, name, path, content, type, hex) VALUES (%s,%s,%s,%s,%s,%s) 
                           ON CONFLICT (id) DO UPDATE 
                               SET name = excluded.name, 
                                   path = excluded.path,
                                   content = excluded.content,
                                   type = excluded.type,
                                   hex = excluded.hex;
                            """,
                        row_data)

        self.update_version('programs')

    def remove_program(self, program):
        row_data = (program,)
        self.run_query("DELETE FROM uscope.programs WHERE id = %s", row_data)

        self.update_version('programs')

    def get_program_hash(self):
        return self.get_version('programs')
