import os
import redis

class RedisClient:
    def __init__(self):
        self.r = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=6379, db=0)