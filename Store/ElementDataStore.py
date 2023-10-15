# Copyright 2021 University of Nottingham Ningbo China
# Author: Filippo Savi <filssavi@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import copy
from sqlalchemy.orm import declarative_base, sessionmaker

from sqlalchemy import create_engine

from .Elements import Peripherals, Programs, Applications, Scripts, UserDataElement, Bitstreams, Filters, Emulator


class ElementsDataStore:

    def __init__(self, host):

        self.engine = create_engine(host)

        self.table_add_id("applications")
        self.table_add_id("peripherals")

        Base = declarative_base()

        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        self.ude = UserDataElement.UserDataElement(self.Session)

    def table_add_id(self, table):
        test_query = "SELECT column_name FROM information_schema.columns WHERE table_name='{table_name}' and column_name='id';".format(
            table_name=table)
        add_column_query = "ALTER TABLE {table_name} ADD COLUMN id SERIAL;".format(table_name=table)
        drop_key = "alter table {table_name} drop constraint {table_name}_pk;".format(table_name=table)
        add_key = "alter table {table_name} add constraint {table_name}_pk primary key (id);".format(table_name=table)
        with self.engine.connect() as con:
            if len(con.execute(test_query).all()) == 0:
                con.execute(add_column_query)
                con.execute(drop_key)
                con.execute(add_key)

    # APPLICATIONS

    def add_application(self, app):
        misc_app = copy.copy(app)

        entries_to_remove = ('application_name', 'bitstream', 'clock_frequency', 'channels', 'channel_groups',
                             'initial_registers_values', 'macro', 'parameters', 'peripherals', 'soft_cores',
                             'filters', 'scripts', 'programs', 'id')
        for k in entries_to_remove:
            misc_app.pop(k, None)

        item = Applications.Applications(id=app['id'], application_name=app["application_name"],
                                         bitstream=app['bitstream'],
                                         clock_frequency=app['clock_frequency'], channels=app['channels'],
                                         channel_groups=app['channel_groups'], miscellaneous=misc_app,
                                         initial_registers_values=app['initial_registers_values'], macro=app['macro'],
                                         parameters=app['parameters'], peripherals=app['peripherals'],
                                         soft_cores=app['soft_cores'], filters=app['filters'], scripts=app['scripts'],
                                         programs=app['programs'])

        self.ude.add_element(item, Applications.Applications)

    def edit_application(self, app):
        self.ude.remove_element(Applications.Applications, 'id', app["id"])
        self.add_application(app)

    def get_applications_dict(self):
        return self.ude.get_elements_dict(Applications.Applications, Applications.application_from_row,
                                          'id')

    def get_application(self, id):
        return self.ude.get_element(Applications.Applications, "id", id,
                                    Applications.application_from_row)

    def remove_application(self, name):
        self.ude.remove_element(Applications.Applications, 'id', name)

    # SCRIPTS
    def get_script(self, script_id):
        return self.ude.get_element(Scripts.Scripts, "id", script_id, Scripts.script_from_row)

    def get_scripts_dict(self):
        return self.ude.get_elements_dict(Scripts.Scripts, Scripts.script_from_row, 'id')

    def add_script(self, script):
        item = Scripts.Scripts(id=script["id"], name=script['name'],
                               content=script['script_content'], triggers=script['triggers'])

        self.ude.add_element(item, Scripts.Scripts)

    def edit_script(self, script):
        self.remove_script(script["id"])
        self.add_script(script)

    def remove_script(self, script):
        self.ude.remove_element(Scripts.Scripts, 'id', script)

    # PROGRAMS
    def get_program(self, id):
        return self.ude.get_element(Programs.Programs, "id", id, Programs.program_from_row)

    def get_programs_dict(self):
        return self.ude.get_elements_dict(Programs.Programs, Programs.program_from_row, 'id')

    def add_program(self, program):
        if 'hex' in program:
            hex_field = program['hex']
        else:
            hex_field = []

        item = Programs.Programs(id=program["id"], name=program['name'],
                                 content=program['program_content'],
                                 type=program['program_type'], hex=hex_field,
                                 build_settings=program['build_settings'],
                                 cached_bin_version=program['cached_bin_version'])

        self.ude.add_element(item, Programs.Programs)

    def edit_program(self, program):
        self.remove_program(program["id"])
        self.add_program(program)

    def remove_program(self, program):
        self.ude.remove_element(Programs.Programs, 'id', program)

    # PERIPHERALS

    def get_peripherals_dict(self):
        return self.ude.get_elements_dict(Peripherals.Peripherals, Peripherals.peripheral_from_row, 'id')

    def get_peripheral(self, name):
        return self.ude.get_element(Peripherals.Peripherals, "id", name, Peripherals.peripheral_from_row)

    def add_peripheral(self, periph: dict):
        item = Peripherals.Peripherals(id=periph['id'], name=periph["peripheral_name"], image=periph['image'],
                                       version=periph['version'], registers=periph['registers'],
                                       parametric=periph['parametric'])

        self.ude.add_element(item, Peripherals.Peripherals)

    def edit_peripheral(self, periph):
        self.remove_peripheral(periph["id"])
        self.add_peripheral(periph)

    def remove_peripheral(self, peripheral):
        self.ude.remove_element(Peripherals.Peripherals, 'id', peripheral)

    # VERSIONS

    def get_peripherals_hash(self):
        return str(self.ude.get_version(Peripherals.Peripherals))

    def get_applications_hash(self):
        return str(self.ude.get_version(Applications.Applications))

    def get_scripts_hash(self):
        return str(self.ude.get_version(Scripts.Scripts))

    def get_program_hash(self):
        return str(self.ude.get_version(Programs.Programs))

    def get_bitstreams_hash(self):
        return str(self.ude.get_version(Bitstreams.Bitstreams))

    def get_filters_hash(self):
        return str(self.ude.get_version(Filters.Filters))

    def get_emulators_hash(self):
        return str(self.ude.get_version(Emulator.Emulator))

    # BITSTREAMS

    def get_bitstreams_dict(self):
        return self.ude.get_elements_dict(Bitstreams.Bitstreams, Bitstreams.bitstream_from_row, 'id')

    def get_bitstream(self, id):
        return self.ude.get_element(Bitstreams.Bitstreams, "id", id, Bitstreams.bitstream_from_row)

    def add_bitstream(self, bitstream: dict):
        item = Bitstreams.Bitstreams(id=bitstream['id'], path=bitstream['path'])
        self.ude.add_element(item, Bitstreams.Bitstreams)

    def edit_bitstream(self, bitstream):
        self.remove_bitstream(bitstream["id"])
        self.add_bitstream(bitstream)

    def remove_bitstream(self, bitstream_id):
        self.ude.remove_element(Bitstreams.Bitstreams, 'id', bitstream_id)

    # FILTERS
    def get_filters_dict(self):
        return self.ude.get_elements_dict(Filters.Filters, Filters.filter_from_row, 'id')

    def get_filter(self, id):
        return self.ude.get_element(Filters.Filters, "id", id, Filters.filter_from_row)

    def add_filter(self, flt: dict):
        if "ideal_taps" in flt:
            id_taps = flt["ideal_taps"]
        else:
            id_taps = []

        if "quantized_taps" in flt:
            q_taps = flt["quantized_taps"]
        else:
            q_taps = []

        item = Filters.Filters(id=flt["id"], name=flt["name"], parameters=flt["parameters"], ideal_taps=id_taps,
                               quantized_taps=q_taps)
        self.ude.add_element(item, Filters.Filters)

    def edit_filter(self, filter_obj):
        self.remove_filter(filter_obj["id"])
        self.add_filter(filter_obj)

    def remove_filter(self, flt_id: dict):
        self.ude.remove_element(Filters.Filters, 'id', flt_id)

    # EMULATORS
    def get_emulators_dict(self):
        return self.ude.get_elements_dict(Emulator.Emulator, Emulator.emulator_from_row, 'id')

    def get_emulator(self, emu_id):
        return self.ude.get_element(Emulator.Emulator, "id", emu_id, Emulator.emulator_from_row)

    def add_emulator(self, emu: dict):
        item = Emulator.Emulator(id=emu["id"], name=emu["name"], connections=emu["connections"], cores=emu["cores"],
                                 inputs=emu["inputs"], outputs=emu["outputs"])
        self.ude.add_element(item, Emulator.Emulator)

    def edit_emulator(self, emulator_obj):
        self.remove_emulator(emulator_obj["id"])
        self.add_emulator(emulator_obj)

    def remove_emulator(self, name):
        self.ude.remove_element(Emulator.Emulator, 'id', name)

    def dump(self):
        dump = {'applications': self.ude.dump(Applications.Applications, Applications.application_from_row),
                'peripherals': self.ude.dump(Peripherals.Peripherals, Peripherals.peripheral_from_row),
                'scripts': self.ude.dump(Scripts.Scripts, Scripts.script_from_row),
                'programs': self.ude.dump(Programs.Programs, Programs.program_from_row),
                'bitstreams': self.ude.dump(Bitstreams.Bitstreams, Bitstreams.bitstream_from_row),
                'filters': self.ude.dump(Filters.Filters, Filters.filter_from_row),
                'emulators': self.ude.dump(Emulator.Emulator, Emulator.emulator_from_row)
                }
        return dump

    def restore(self, data):

        for app in data['applications']:
            self.remove_application(app['application_name'])
            self.add_application(app)

        for periph in data['peripherals']:
            self.remove_peripheral(periph['peripheral_name'])
            self.add_peripheral(periph)

        for script in data['scripts']:
            self.remove_script(script['id'])
            self.add_script(script)

        for prog in data['programs']:
            self.remove_program(prog['id'])
            self.add_program(prog)

        for bitstream in data['bitstreams']:
            self.remove_bitstream(bitstream['id'])
            self.add_bitstream(bitstream)

        for filter_obj in data['filters']:
            self.remove_filter(filter_obj['id'])
            self.add_filter(filter_obj)

        for emulator_obj in data['emulators']:
            self.remove_emulator(emulator_obj["name"])
            self.add_emulator(emulator_obj)
