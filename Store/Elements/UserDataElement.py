from sqlalchemy import Column, String
from .OrmBase import Base
from sqlalchemy.dialects import postgresql

import uuid
import datetime


class Versions(Base):

    __tablename__ = 'data_versions'

    table = Column(String, primary_key=True)
    version = Column(postgresql.UUID(as_uuid=True))
    last_modified = Column(postgresql.TIMESTAMP)

    def __repr__(self):
        return "<Version(table='%s', version='%s', last_modified='%s')>" % (
                             self.table, self.version, self.last_modified)


class UserDataElement:

    def __init__(self, sesssion):
        self.Session = sesssion

    def get_row(self, table, filter_name, filter_value):
        with self.Session() as session:
            return session.query(table).filter(getattr(table, filter_name) == filter_value).first()

    def get_element(self, table, filter_name, filter_value, creator_func):
        try:
            return creator_func(self.get_row(table,filter_name,filter_value))
        except AttributeError:
            raise KeyError('Element Not Found')

    def get_elements_dict(self, table, creator_func, key):
        with self.Session() as session:
            with session.begin():
                result = session.query(table).all()
                scripts = {}
                for row in result:
                    scripts[getattr(row, key)] = creator_func(row)
        return scripts

    def add_element(self, item, table):
        with self.Session() as session:
            with session.begin():
                session.add(item)
                self.update_version(table)

    def remove_element(self, table, filter_name, filter_value):
        element = self.get_row(table, filter_name, filter_value)
        if element:
            with self.Session() as session:
                with session.begin():
                    session.delete(element)
                    self.update_version(table)

    def update_version(self, table):
        with self.Session() as session:
            with session.begin():
                version = session.query(Versions).filter_by(table=table.VersionTableName).first()
                if version:
                    version.version = uuid.uuid4()
                    version.last_modified = datetime.datetime.now()
                else:
                    item = Versions(table=table.VersionTableName, version=uuid.uuid4(), last_modified=datetime.datetime.now())
                    session.add(item)

    def get_version(self, table):
        with self.Session() as session:
            with session.begin():
                version = session.query(Versions).filter_by(table=table.VersionTableName).first()
                return version.version

    def dump(self, table, creator_func):
        with self.Session() as session:
            with session.begin():
                result = session.query(table).all()
                dump = []
                for row in result:
                    dump.append(creator_func(row))
        return dump
