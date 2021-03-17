from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects import postgresql

from sqlalchemy import create_engine

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