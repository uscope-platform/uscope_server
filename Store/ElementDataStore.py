
from sqlalchemy.orm import declarative_base, sessionmaker

from sqlalchemy import create_engine

from .Elements import Peripherals, Programs, Applications, Scripts, UserDataElement


class ElementsDataStore:

    def __init__(self, host=None):
        if host:
            self.engine = create_engine("postgresql+psycopg2://uscope:test@" + host + "/uscope")
        else:
            self.engine = create_engine("postgresql+psycopg2://uscope:test@database/uscope")

        Base = declarative_base()

        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        self.ude = UserDataElement.UserDataElement(self.Session)

        # UPDATE VERSIONS
        self.ude.update_version(Applications.Applications)
        self.ude.update_version(Scripts.Scripts)
        self.ude.update_version(Programs.Programs)
        self.ude.update_version(Peripherals.Peripherals)

    # APPLICATIONS

    def add_application(self, app):
        item = Applications.Applications(application_name=app["application_name"], bitstream=app['bitstream'],
                                         clock_frequency=app['clock_frequency'], channels=app['channels'],
                                         channel_groups=app['channel_groups'],
                                         initial_registers_values=app['initial_registers_values'], macro=app['macro'],
                                         parameters=app['parameters'], peripherals=app['peripherals']
                                         )
        self.ude.add_element(item, Applications.Applications)

    def get_applications_dict(self):
        return self.ude.get_elements_dict(Applications.Applications, Applications.application_from_row, 'application_name')

    def get_application(self, name):
        return self.ude.get_element(Applications.Applications, "application_name", name, Applications.application_from_row)

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

    def remove_script(self, script):
        self.ude.remove_element(Scripts.Scripts, 'id', script)

    # PROGRAMS
    def get_program(self, id):
        return self.ude.get_element(Programs.Programs, "id", id, Programs.program_from_row)

    def get_programs_dict(self):
        return self.ude.get_elements_dict(Programs.Programs, Programs.program_from_row, 'id')

    def add_program(self, program):
        item = Programs.Programs(id=program["id"], name=program['name'],
                                 content=program['program_content'], path=program['path'],
                                 type=program['program_type'], hex=program['hex'])

        self.ude.add_element(item, Programs.Programs)

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
