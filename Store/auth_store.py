import redis
import json

class AuthStore:
    def __init__(self, redis_host):
        self.redis_if = redis.Redis(host=redis_host, port=6379, db=5, charset="utf-8", decode_responses=True)

    # PERIPHERALS

    def add_user(self, username, content):
        self.redis_if.hset('Users', username, json.dumps(content))

    def user_exists(self, username):
        return self.redis_if.hexists('Users', username)

    def get_password_hash(self, username):
        content = json.loads(self.redis_if.hget('Users', username))
        return content['pw_hash']

    def remove_user(self, username):
        self.redis_if.hdel('Users', username)

    def get_token(self, selector):
        return json.loads(self.redis_if.hget('Tokens', selector))

    def add_token(self, selector, token_obj):
        self.redis_if.hset('Tokens', selector, json.dumps(token_obj))

    def remove_token(self, username):
        pass