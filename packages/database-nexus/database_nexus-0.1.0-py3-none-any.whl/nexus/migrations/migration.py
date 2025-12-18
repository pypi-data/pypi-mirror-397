#𝖇𝖞 𝖊𝖑𝖎7𝖊𝖎𝖓 - 𝕰7

from abc import ABC, abstractmethod


class Migration(ABC):
    @abstractmethod
    async def up(self):
        pass

    @abstractmethod
    async def down(self):
        pass