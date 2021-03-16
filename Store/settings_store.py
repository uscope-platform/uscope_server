import psycopg2.extras
from sqlalchemy import create_engine


class SettingsStore:
    def __init__(self):
        self.db_engine = create_engine("postgresql+psycopg2://uscope:test@database/uscope")
        self.clear_settings()

    def run_select_one(self, query, data):
        with self.db_engine.connect() as connection:
            result = connection.execute(query, data)
            result = result.fetchone()
        return result

    def run_query(self, query, data):
        with self.db_engine.connect() as connection:
            connection.execute(query, data)

    def get_value(self, name):
        res = self.run_select_one('SELECT value FROM uscope.app_settings WHERE name LIKE (%s)', (name,))
        return res[0]

    def set_value(self, name, value):
        row_data = (name, psycopg2.extras.Json(value))
        self.run_query("""INSERT INTO uscope.app_settings (name, value) VALUES (%s,%s)
                                   ON CONFLICT (name) DO UPDATE 
                                       SET value = excluded.value;""", row_data)

    def clear_settings(self):
        self.run_query('DELETE FROM uscope.app_settings', ())
