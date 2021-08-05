import redis
import json


class SettingsStore:
    def __init__(self, clear_settings=True, host='redis'):
        self.redis = redis.Redis(host=host, port=6379, db=0)
        if clear_settings:
            self.clear_settings()

    def get_value(self, name, username):
        return json.loads(self.redis.get(name+username))

    def set_value(self, name, value, username):
        self.redis.set(name+username, json.dumps(value))

    def clear_settings(self):
        print("CLEARED SETTINGS")
        self.redis.flushdb()

    def dump(self):
        pass

    def restore(self, data):
        pass