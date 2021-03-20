from sqlalchemy import Column, String
from .OrmBase import Base
from sqlalchemy.dialects import postgresql


class Applications(Base):
    __tablename__ = 'applications'

    VersionTableName = 'Applications'

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


def application_from_row(row : Applications):
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

