import time as system_time
import logging

class SimpleCache:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache = {}
        self.cache_expiration = {}

    def set(self, key, value, time=None):
        self.logger.info(f"Set cache: key: {key} | value: {value.__class__.__name__} | time: {time}")
        self.cache[key] = value
        if time:
            self.cache_expiration[key] = system_time.time() + time
        
    def get(self, key):
        self.logger.info(f"Getting cache for key: {key}")
        if key in self.cache_expiration and system_time.time() > self.cache_expiration[key]:
            del self.cache[key]
            del self.cache_expiration[key]
            return None
        
        value = self.cache.get(key)

        if value is None:
            self.logger.info(f"Cache MISS for key: {key}")
        else:
            self.logger.info(f"Cache HIT for key: {key}")

        return value