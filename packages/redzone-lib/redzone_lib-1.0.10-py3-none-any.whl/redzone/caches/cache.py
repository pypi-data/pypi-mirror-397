from microgue.asynchronous.caches.abstract_cache import AbstractCache

from ..settings import CACHE_HOST, CACHE_PREFIX


class Cache(AbstractCache):
    host = CACHE_HOST
    prefix = f"{CACHE_PREFIX}"
