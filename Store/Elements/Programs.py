from sqlalchemy import Column, String, Integer, BigInteger
from .OrmBase import Base
from sqlalchemy.dialects import postgresql


class Programs(Base):
    __tablename__ = 'programs'

    VersionTableName = 'programs'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    path = Column(String)
    content = Column(String)
    type = Column(String)
    hex = Column(postgresql.ARRAY(BigInteger))

    def __repr__(self):
        return "<Program(id='%s', name='%s', content='%s')>" % (
                             self.id, self.name, self.content)


def program_from_row(row):
    return {'id': row.id, 'name': row.name, 'path': row.path, 'program_content': row.content,
            'program_type': row.type, 'hex': row.hex}
