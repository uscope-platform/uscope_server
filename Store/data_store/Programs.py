from sqlalchemy import Column, String, Integer, BigInteger
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects import postgresql

# declarative base class
Base = declarative_base()

class Programs(Base):
    __tablename__ = 'programs'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    path = Column(String)
    content = Column(String)
    type = Column(String)
    hex = Column(postgresql.ARRAY(BigInteger))

    def __repr__(self):
        return "<Program(id='%s', name='%s', content='%s')>" % (
                             self.id, self.name, self.content)
