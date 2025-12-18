#𝖇𝖞 𝖊𝖑𝖎7𝖊𝖎𝖓 - 𝕰7

from typing import Dict, Any, Optional, Type, List
from .model import Model
from .query import Query
from .exceptions import DatabaseError, ConnectionError

_databases: Dict[str, "Database"] = {}


class Database:
    def __init__(self, url: str, name: str = "default", **kwargs):
        self.url = url
        self.name = name
        self.kwargs = kwargs
        self.connection = None

        # Автоматически регистрируем базу данных
        register_database(name, self)

    async def connect(self):
        if self.url.startswith("sqlite://"):
            from ..backends.sqlite import SQLiteBackend
            self.backend = SQLiteBackend(self.url, **self.kwargs)
        elif self.url.startswith("postgresql://"):
            from ..backends.postgresql import PostgreSQLBackend
            self.backend = PostgreSQLBackend(self.url, **self.kwargs)
        else:
            raise ConnectionError(f"Unsupported database URL: {self.url}")

        await self.backend.connect()
        self.connection = self.backend

    async def disconnect(self):
        if self.connection:
            await self.connection.disconnect()

    async def create_table(self, model: Type[Model]):
        return await self.connection.create_table(model)

    async def save(self, instance: Model):
        return await self.connection.save(instance)

    async def delete(self, instance: Model):
        return await self.connection.delete(instance)

    def query(self, model: Type[Model]):
        return Query(model, self.connection)


def get_database(name: str = "default") -> Optional[Database]:
    return _databases.get(name)


def register_database(name: str, database: Database):
    _databases[name] = database