from sqlalchemy import Column, String, Integer
from .OrmBase import Base


class Bitstreams(Base):
    __tablename__ = 'bitstreams'

    VersionTableName = 'bitstreams'

    id = Column(Integer, primary_key=True)
    path = Column(String)


    def __repr__(self):
        return "<Script(id='%s', path='%s')>" % (
                             self.id, self.path)

def bitstream_from_row(row):
    return {'id': row.id, 'path': row.path}