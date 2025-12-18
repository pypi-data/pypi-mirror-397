#𝖇𝖞 𝖊𝖑𝖎7𝖊𝖎𝖓 - 𝕰7

from typing import Type, Any, Optional, List, Union
from .model import Model


class Query:
    def __init__(self, model: Type[Model], connection):
        self.model = model
        self.connection = connection
        self._where = []
        self._limit = None
        self._offset = None
        self._order_by = []
        self._select = []

    def where(self, condition):
        self._where.append(condition)
        return self

    def limit(self, n: int):
        self._limit = n
        return self

    def offset(self, n: int):
        self._offset = n
        return self

    def order_by(self, field: str, direction: str = "ASC"):
        self._order_by.append((field, direction))
        return self

    def select(self, *fields):
        self._select.extend(fields)
        return self

    async def all(self) -> List[Model]:
        return await self.connection.execute_query(self)

    async def first(self) -> Optional[Model]:
        self._limit = 1
        results = await self.all()
        return results[0] if results else None

    async def count(self) -> int:
        return await self.connection.count(self)

    async def delete(self) -> int:
        return await self.connection.delete_query(self)