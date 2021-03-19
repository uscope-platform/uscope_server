from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'

    username = Column(String, primary_key=True)
    pw_hash = Column(String)

    def __repr__(self):
        return "<User(username='%s', pw_hash='%s')>" % (
                             self.username, self.pw_hash)

