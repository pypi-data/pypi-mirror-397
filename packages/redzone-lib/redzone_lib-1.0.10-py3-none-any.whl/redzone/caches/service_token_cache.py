from ..caches.cache import Cache


class ServiceTokenCache(Cache):
    prefix = f"{Cache.prefix}-service-token"
    ttl = 43200  # 12 hours in seconds
    connection_required = False
