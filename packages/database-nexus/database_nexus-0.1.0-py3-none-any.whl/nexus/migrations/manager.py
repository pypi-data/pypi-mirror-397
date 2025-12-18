#𝖇𝖞 𝖊𝖑𝖎7𝖊𝖎𝖓 - 𝕰7

import importlib
import os
from typing import List
from .engine import MigrationEngine


class MigrationManager:
    def __init__(self, database, migrations_path: str = "migrations"):
        self.database = database
        self.migrations_path = migrations_path
        self.engine = MigrationEngine(database)

    async def migrate(self):
        await self.engine.initialize()
        applied = await self.engine.get_applied_migrations()

        migration_files = self._get_migration_files()
        for migration_file in migration_files:
            if migration_file not in applied:
                await self._apply_migration(migration_file)

    async def rollback(self, steps: int = 1):
        applied = await self.engine.get_applied_migrations()
        for i in range(steps):
            if not applied:
                break
            migration_file = applied.pop()
            await self._rollback_migration(migration_file)

    def _get_migration_files(self) -> List[str]:
        if not os.path.exists(self.migrations_path):
            return []

        files = []
        for file in os.listdir(self.migrations_path):
            if file.endswith(".py") and file != "__init__.py":
                files.append(file.replace(".py", ""))

        return sorted(files)

    async def _apply_migration(self, migration_name: str):
        module = importlib.import_module(f"{self.migrations_path}.{migration_name}")
        migration_class = getattr(module, f"Migration{migration_name.replace('_', '')}")
        migration = migration_class()
        await migration.up()
        await self.engine.mark_migration_applied(migration_name)

    async def _rollback_migration(self, migration_name: str):
        module = importlib.import_module(f"{self.migrations_path}.{migration_name}")
        migration_class = getattr(module, f"Migration{migration_name.replace('_', '')}")
        migration = migration_class()
        await migration.down()
        await self.engine.mark_migration_rolled_back(migration_name)