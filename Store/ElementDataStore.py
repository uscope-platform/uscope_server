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

from .Elements import Peripherals, Programs, Applications, Scripts, UserDataElement, Bitstreams


class ElementsDataStore:

    def __init__(self, host, update_ude_versions_on_init=True):

        self.engine = create_engine(host)

        Base = declarative_base()

        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        self.ude = UserDataElement.UserDataElement(self.Session)

        # UPDATE VERSIONS
        if update_ude_versions_on_init:
            self.ude.update_version(Applications.Applications)
            self.ude.update_version(Scripts.Scripts)
            self.ude.update_version(Programs.Programs)
            self.ude.update_version(Peripherals.Peripherals)
            self.ude.update_version(Bitstreams.Bitstreams)

    # APPLICATIONS

    def add_application(self, app):
        misc_app = copy.copy(app)

        entries_to_remove = ('application_name', 'bitstream', 'clock_frequency', 'channels', 'channel_groups',
                             'initial_registers_values', 'macro', 'parameters', 'peripherals')
        for k in entries_to_remove:
            misc_app.pop(k, None)
        item = Applications.Applications(application_name=app["application_name"], bitstream=app['bitstream'],
                                         clock_frequency=app['clock_frequency'], channels=app['channels'],
                                         channel_groups=app['channel_groups'], miscellaneous=misc_app,
                                         initial_registers_values=app['initial_registers_values'], macro=app['macro'],
                                         parameters=app['parameters'], peripherals=app['peripherals'])

        self.ude.add_element(item, Applications.Applications)

    def edit_application(self, app):
        self.ude.remove_element(Applications.Applications, 'application_name', app["application_name"])
        self.add_application(app)

    def get_applications_dict(self):
        return self.ude.get_elements_dict(Applications.Applications, Applications.application_from_row,
                                          'application_name')

    def get_application(self, name):
        return self.ude.get_element(Applications.Applications, "application_name", name,
                                    Applications.application_from_row)

    def remove_application(self, name):
        self.ude.remove_element(Applications.Applications, 'application_name', name)

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
                                 content=program['program_content'], type=program['program_type'], hex=hex_field)

        self.ude.add_element(item, Programs.Programs)

    def edit_program(self, program):
        self.remove_program(program["id"])
        self.add_program(program)

    def remove_program(self, program):
        self.ude.remove_element(Programs.Programs, 'id', program)

    # PERIPHERALS

    def get_peripherals_dict(self):
        return self.ude.get_elements_dict(Peripherals.Peripherals, Peripherals.peripheral_from_row, 'name')

    def get_peripheral(self, name):
        return self.ude.get_element(Peripherals.Peripherals, "name", name, Peripherals.peripheral_from_row)

    def add_peripheral(self, periph: dict):
        item = Peripherals.Peripherals(name=periph["peripheral_name"], image=periph['image'],
                                       version=periph['version'], registers=periph['registers'])

        self.ude.add_element(item, Peripherals.Peripherals)

    def edit_peripheral(self, periph):
        self.remove_peripheral(periph["peripheral_name"])
        self.add_peripheral(periph)

    def remove_peripheral(self, peripheral):
        self.ude.remove_element(Peripherals.Peripherals, 'name', peripheral)

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

    # BITSTREAMS

    def get_bitstreams_dict(self):
        return self.ude.get_elements_dict(Bitstreams.Bitstreams, Bitstreams.bitstream_from_row,  'id')

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

    def dump(self):
        dump = {'applications': self.ude.dump(Applications.Applications, Applications.application_from_row),
                'peripherals': self.ude.dump(Peripherals.Peripherals, Peripherals.peripheral_from_row),
                'scripts': self.ude.dump(Scripts.Scripts, Scripts.script_from_row),
                'programs': self.ude.dump(Programs.Programs, Programs.program_from_row),
                'bitstreams': self.ude.dump(Bitstreams.Bitstreams, Bitstreams.bitstream_from_row)
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
