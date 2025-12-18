#𝖇𝖞 𝖊𝖑𝖎7𝖊𝖎𝖓 - 𝕰7

from .base import BaseBackend
from ..core.exceptions import DatabaseError


class RedisBackend(BaseBackend):
    def __init__(self, url: str, **kwargs):
        self.url = url
        self.kwargs = kwargs

    async def connect(self):
        raise NotImplementedError("Redis backend not implemented yet")

    async def disconnect(self):
        pass

    async def create_table(self, model):
        raise NotImplementedError("Redis backend not implemented yet")

    async def save(self, instance):
        raise NotImplementedError("Redis backend not implemented yet")

    async def delete(self, instance):
        raise NotImplementedError("Redis backend not implemented yet")

    async def execute_query(self, query):
        raise NotImplementedError("Redis backend not implemented yet")

    async def count(self, query):
        raise NotImplementedError("Redis backend not implemented yet")

    async def delete_query(self, query):
        raise NotImplementedError("Redis backend not implemented yet")