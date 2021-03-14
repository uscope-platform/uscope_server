import psycopg2
import datetime as dt


class AuthStore:
    def __init__(self):
        self.pg_db = psycopg2.connect("dbname=uscope user=uscope password=test host=database")
        self.db = self.pg_db.cursor()

    def __del__(self):
        self.pg_db.close()

    # PERIPHERALS

    def add_user(self, username, content):
        row_data = (content['username'], content['pw_hash'])
        self.db.execute("INSERT INTO uscope.users (username, pw_hash) VALUES (%s, %s);", row_data)
        self.pg_db.commit()

    def user_exists(self, username):
        row_data = (username,)
        self.db.execute("SELECT COUNT(1) FROM uscope.users WHERE username LIKE (%s) ESCAPE '#';", row_data)
        return self.db.fetchone()[0] == 1

    def get_password_hash(self, username):
        row_data = (username,)
        self.db.execute("SELECT pw_hash FROM uscope.users WHERE username LIKE (%s) ESCAPE '#';", row_data)
        pw_hash = self.db.fetchone()[0]
        self.pg_db.commit()
        return pw_hash

    def remove_user(self, username):
        row_data = (username,)
        self.db.execute("DELETE FROM uscope.users WHERE username LIKE %s", row_data)
        self.pg_db.commit()

    def get_token(self, selector):
        row_data = (selector,)
        self.db.execute("SELECT * FROM uscope.login_tokens WHERE selector like %s", row_data)
        token = self.db.fetchone()
        self.pg_db.commit()
        return {'username': token[0], 'expiry': token[1].timestamp(), 'validator': token[2]}

    def add_token(self, selector, token_obj):
        timestamp = dt.datetime.fromtimestamp(token_obj['expiry'])
        row_data = (token_obj['username'], timestamp, token_obj['validator'], selector)
        self.db.execute(
            "INSERT INTO uscope.login_tokens (username, expiry, validator, selector) VALUES (%s, %s, %s, %s);",
            row_data)
        self.pg_db.commit()

    def remove_token(self, username):
        pass
