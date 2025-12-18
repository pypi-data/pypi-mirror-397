#𝖇𝖞 𝖊𝖑𝖎7𝖊𝖎𝖓 - 𝕰7

from typing import List, Dict, Any
import os


class MigrationEngine:
    def __init__(self, database):
        self.database = database

    async def initialize(self):
        sql = """
        CREATE TABLE IF NOT EXISTS nexus_migrations (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        await self.database.connection.execute(sql)

    async def get_applied_migrations(self) -> List[str]:
        sql = "SELECT name FROM nexus_migrations ORDER BY applied_at"
        results = await self.database.connection.fetch(sql)
        return [row["name"] for row in results]

    async def mark_migration_applied(self, name: str):
        sql = "INSERT INTO nexus_migrations (name) VALUES ($1)"
        await self.database.connection.execute(sql, name)

    async def mark_migration_rolled_back(self, name: str):
        sql = "DELETE FROM nexus_migrations WHERE name = $1"
        await self.database.connection.execute(sql, name)