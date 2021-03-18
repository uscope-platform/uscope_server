from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects import postgresql
from sqlalchemy import select

# declarative base class
Base = declarative_base()


class Applications(Base):
    __tablename__ = 'applications'

    application_name = Column(String, primary_key=True)
    bitstream = Column(String)
    clock_frequency = Column(String)
    channels = Column(postgresql.JSONB)
    channel_groups = Column(postgresql.JSONB)
    initial_registers_values = Column(postgresql.JSONB)
    macro = Column(postgresql.JSONB)
    parameters = Column(postgresql.JSONB)
    peripherals = Column(postgresql.JSONB)
    miscellaneous = Column(postgresql.JSONB)


    def __repr__(self):
        return "<Application(application_name='%s', bitstream='%s')>" % (
                             self.application_name, self.bitstream)


class ApplicationsStore:

    def __init__(self, sesssion):
        self.Session = sesssion


    def application_from_row(self, row : Applications):
        app = {}
        app['application_name'] = row.application_name
        app['bitstream'] = row.bitstream
        app['clock_frequency'] = row.clock_frequency
        app['channels'] = row.channels
        app['channel_groups'] = row.channel_groups
        app['initial_registers_values'] = row.initial_registers_values
        app['macro'] = row.macro
        app['parameters'] = row.parameters
        app['peripherals'] = row.peripherals
        for i in row.miscellaneous:
            app[i] = row.miscellaneous[i]
        return app

    def add_application(self, app):
        item = Applications(application_name=app["application_name"], bitstream=app['bitstream'],
                            clock_frequency=app['clock_frequency'], channels=app['channels'],
                            channel_groups=app['channel_groups'],
                            initial_registers_values=app['initial_registers_values'], macro=app['macro'],
                            parameters=app['parameters'], peripherals = app['peripherals']
                            )
        with self.Session() as session:
            with session.begin():
                session.add(item)

    def get_applications_dict(self):
        with self.Session() as session:
            with session.begin():
                result = session.query(Applications).all()
                apps = {}
                for row in result:
                    apps[row.application_name] = self.application_from_row(row)
        return apps

    def get_application(self, name):
        try:
            with self.Session() as session:
                result = session.query(Applications).filter_by(application_name=name).first()
            return self.application_from_row(result)
        except AttributeError:
            raise KeyError('Application Not Found')

    def remove_application(self, name):
        try:
            with self.Session() as session:
                application = session.query(Applications).filter_by(application_name=name).first()
        except AttributeError:
            raise KeyError('Application Not Found')

        with self.Session() as session:
            with session.begin():
                session.delete(application)
