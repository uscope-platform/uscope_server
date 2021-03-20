import datetime as dt

from sqlalchemy.orm import declarative_base, sessionmaker

from sqlalchemy import create_engine
from .Elements import Users


class AuthStore:
    def __init__(self, host=None):
        if host:
            self.engine = create_engine("postgresql+psycopg2://uscope:test@" + host + "/uscope")
        else:
            self.engine = create_engine("postgresql+psycopg2://uscope:test@database/uscope")

        Base = declarative_base()
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        self.auth_db = Users.AuthenticationDatabase(self.Session)

    # PERIPHERALS

    def add_user(self, username, content):
        self.auth_db.add_user(content['username'], content['pw_hash'])

    def user_exists(self, username):
        self.auth_db.user_exists(username)

    def get_password_hash(self, username):
        return self.auth_db.get_password_hash(username)

    def remove_user(self, username):
        self.auth_db.remove_user(username)

    def get_token(self, selector):
        token = self.auth_db.get_token(selector)
        return {'username': token.username, 'expiry': token.expiry.timestamp(), 'validator': token.validator}

    def add_token(self, selector, token_obj):
        timestamp = dt.datetime.fromtimestamp(token_obj['expiry'])
        self.auth_db.add_token(token_obj['username'], timestamp, token_obj['validator'], selector)

    def remove_token(self, username):
        pass
