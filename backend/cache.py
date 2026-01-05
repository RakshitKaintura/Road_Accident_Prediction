import time

_cache = {}

def get_cache(key):
    entry = _cache.get(key)
    if not entry:
        return None
    value, expiry = entry
    if time.time() > expiry:
        del _cache[key]
        return None
    return value

def set_cache(key, value, ttl):
    _cache[key] = (value, time.time() + ttl)
