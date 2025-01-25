import time as system_time

class SimpleCache:
    def __init__(self):
        self.cache = {}
        self.cache_expiration = {}

    def set(self, key, value, time=None):
        self.cache[key] = value
        if time:
            self.cache_expiration[key] = system_time.time() + time
        
    def get(self, key):
        if key in self.cache_expiration and system_time.time() > self.cache_expiration[key]:
            del self.cache[key]
            del self.cache_expiration[key]
            return None
        return self.cache.get(key)