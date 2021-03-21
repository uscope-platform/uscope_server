from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects import postgresql
from .OrmBase import Base

class Users(Base):
    __tablename__ = 'users'

    username = Column(String, primary_key=True)
    pw_hash = Column(String)
    tokens = relationship("LoginTokens")
    settings = relationship("Settings")

    def __repr__(self):
        return "<User(username='%s', pw_hash='%s')>" % (
                             self.username, self.pw_hash)


class LoginTokens(Base):
    __tablename__ = 'login_tokens'

    username = Column(String, ForeignKey('users.username'))
    expiry = Column(postgresql.TIMESTAMP)
    validator = Column(String)
    selector = Column(String, primary_key=True)


class AuthenticationDatabase:
    def __init__(self, session):
        self.Session = session

    def get_users_list(self):
        with self.Session() as session:
            with session.begin():
                res = session.query(Users).all()
                users = []
                for row in res:
                    users.append(row.username)
        return users

    def get_password_hash(self, user):
        with self.Session() as session:
            with session.begin():
                res = session.query(Users).filter_by(username=user).first()
                return res.pw_hash

    def user_exists(self, user):
        with self.Session() as session:
            with session.begin():
                return session.query(Users).filter_by(username=user).count() == 1

    def add_user(self, user, pw_hash):
        item = Users(username=user, pw_hash=pw_hash)
        self.add_item(item)

    def remove_user(self, user):
        with self.Session() as session:
            element = session.query(Users).filter_by(username=user).first()
        if element:
            with self.Session() as session:
                with session.begin():
                    session.delete(element)

    def add_item(self, item):
        with self.Session() as session:
            with session.begin():
                session.add(item)

    def add_token(self, user, expiry, validator, selector):
        item = LoginTokens(username=user, expiry=expiry, validator=validator, selector=selector)
        self.add_item(item)

    def get_token(self, selector)-> LoginTokens:
        with self.Session() as session:
            with session.begin():
                tok = session.query(LoginTokens).filter_by(selector=selector).first()
                session.expunge(tok)
                return tok

    def dump(self):
        with self.Session() as session:
            with session.begin():
                result = session.query(Users).all()
                dump = []
                for row in result:
                    dump.append({'username': row.username, 'pw_hash': row.pw_hash})
        return dump


    def restore(self, data):
        pass