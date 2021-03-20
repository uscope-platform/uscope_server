from sqlalchemy import Column, String
from .OrmBase import Base
from sqlalchemy.dialects import postgresql


class Peripherals(Base):
    __tablename__ = 'peripherals'

    VersionTableName = 'Peripherals'

    name = Column(String, primary_key=True)
    image = Column(String)
    version = Column(String)
    registers = Column(postgresql.JSONB)

    def __repr__(self):
        return "<Peripheral(name='%s', image='%s', version='%s')>" % (
                             self.name, self.image, self.version)


def peripheral_from_row(row):
    return {'peripheral_name': row.name, 'image': row.image, 'version': row.version, 'registers': row.registers}
