#𝖇𝖞 𝖊𝖑𝖎7𝖊𝖎𝖓 - 𝕰7

from abc import ABC, abstractmethod
from typing import Type, Any, List


class BaseBackend(ABC):
    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def disconnect(self):
        pass

    @abstractmethod
    async def create_table(self, model: Type[Any]):
        pass

    @abstractmethod
    async def save(self, instance: Any):
        pass

    @abstractmethod
    async def delete(self, instance: Any):
        pass

    @abstractmethod
    async def execute_query(self, query: Any) -> List[Any]:
        pass

    @abstractmethod
    async def count(self, query: Any) -> int:
        pass

    @abstractmethod
    async def delete_query(self, query: Any) -> int:
        pass