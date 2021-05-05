from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects import postgresql
from .OrmBase import Base


class Users(Base):
    __tablename__ = 'users'

    username = Column(String, primary_key=True)
    pw_hash = Column(String)
    role = Column(String)
    tokens = relationship("LoginTokens")

    def __repr__(self):
        return "<User(username='%s', role='%s', pw_hash='%s')>" % (
                             self.username, self.role, self.pw_hash)


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
                    users.append({'username': row.username, 'role': row.role})
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

    def add_user(self, user, pw_hash, role):
        item = Users(username=user, pw_hash=pw_hash, role=role)
        self.add_item(item)

    def get_user(self, username):
        with self.Session() as session:
            with session.begin():
                res = session.query(Users).filter_by(username=username).first()
                return {"pw_hash": res.pw_hash, "role": res.role}

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
                    dump.append({'username': row.username, 'pw_hash': row.pw_hash, 'role': row.role})
        return dump

    def restore(self, data):
        for item in data:
            if not self.user_exists(item['username']):
                self.add_user(item['username'], item['pw_hash'], item['role'])
