#𝖇𝖞 𝖊𝖑𝖎7𝖊𝖎𝖓 - 𝕰7

import aiosqlite
from typing import Type, Any, List, get_origin, get_args
from .base import BaseBackend
from ..core.exceptions import DatabaseError


class SQLiteBackend(BaseBackend):
    def __init__(self, url: str, **kwargs):
        self.url = url.replace("sqlite:///", "")
        self.conn = None

    async def connect(self):
        self.conn = await aiosqlite.connect(self.url)
        self.conn.row_factory = aiosqlite.Row

    async def disconnect(self):
        if self.conn:
            await self.conn.close()

    async def create_table(self, model):
        fields = []
        for name, field in model.__fields__.items():
            field_info = model.get_field_info(name)

            # Получаем тип из аннотаций класса
            field_type = self._get_field_type(model, name)
            constraints = []

            if field_info.get('primary_key'):
                constraints.append("PRIMARY KEY")
                if field_info.get('generated') and field_type == "INTEGER":
                    constraints.append("AUTOINCREMENT")

            if not field_info.get('nullable', True):
                constraints.append("NOT NULL")

            if field_info.get('unique'):
                constraints.append("UNIQUE")

            if constraints:
                fields.append(f"{name} {field_type} {' '.join(constraints)}")
            else:
                fields.append(f"{name} {field_type}")

        sql = f"CREATE TABLE IF NOT EXISTS {model.get_tablename()} ({', '.join(fields)})"
        print(f"DEBUG SQL: {sql}")  # Для отладки
        await self.conn.execute(sql)
        await self.conn.commit()

    def _get_field_type(self, model, field_name):
        # Получаем аннотацию типа из класса модели
        annotations = model.__annotations__
        if field_name in annotations:
            field_type = annotations[field_name]
            return self._map_type(field_type)
        return "TEXT"

    def _map_type(self, python_type):
        # Обработка Optional[T] -> Union[T, None]
        origin = get_origin(python_type)
        if origin is not None:
            # Если это Optional[T] или Union[T, None]
            args = get_args(python_type)
            # Берем первый аргумент, который не None
            for arg in args:
                if arg is not type(None):
                    return self._map_type(arg)
            return "TEXT"

        type_map = {
            str: "TEXT",
            int: "INTEGER",
            float: "REAL",
            bool: "INTEGER",
            type(None): "NULL",
        }

        return type_map.get(python_type, "TEXT")

    async def save(self, instance):
        tablename = instance.__class__.get_tablename()
        fields = []
        values = []

        # Исключаем поля с None значениями для INSERT
        for name in instance.__fields__:
            value = getattr(instance, name)
            if value is not None or name == "id":
                fields.append(name)
                values.append(value)

        has_id = getattr(instance, "id", None) is not None

        if not has_id:
            placeholders = ", ".join(["?" for _ in fields])
            field_names = ", ".join(fields)
            sql = f"INSERT INTO {tablename} ({field_names}) VALUES ({placeholders})"
        else:
            updates = ", ".join([f"{name} = ?" for name in fields])
            sql = f"UPDATE {tablename} SET {updates} WHERE id = ?"
            values.append(instance.id)

        print(f"DEBUG SAVE SQL: {sql}")  # Для отладки
        await self.conn.execute(sql, values)
        await self.conn.commit()

        if not has_id:
            cursor = await self.conn.execute("SELECT last_insert_rowid()")
            row = await cursor.fetchone()
            instance.id = row[0]

        return instance

    async def delete(self, instance):
        tablename = instance.__class__.get_tablename()
        sql = f"DELETE FROM {tablename} WHERE id = ?"
        await self.conn.execute(sql, (getattr(instance, "id"),))
        await self.conn.commit()

    async def execute_query(self, query):
        sql, params = self._build_sql(query)
        cursor = await self.conn.execute(sql, params)
        rows = await cursor.fetchall()

        results = []
        for row in rows:
            data = dict(row)
            results.append(query.model(**data))

        return results

    async def count(self, query):
        sql, params = self._build_sql(query, count=True)
        cursor = await self.conn.execute(sql, params)
        row = await cursor.fetchone()
        return row[0] if row else 0

    async def delete_query(self, query):
        sql, params = self._build_sql(query, delete=True)
        await self.conn.execute(sql, params)
        await self.conn.commit()
        cursor = await self.conn.execute("SELECT changes()")
        row = await cursor.fetchone()
        return row[0] if row else 0

    def _build_sql(self, query, count=False, delete=False):
        tablename = query.model.get_tablename()
        params = []

        if delete:
            sql = f"DELETE FROM {tablename}"
        elif count:
            sql = f"SELECT COUNT(*) FROM {tablename}"
        else:
            sql = f"SELECT * FROM {tablename}"

        if query._where:
            where_conditions = []
            for condition in query._where:
                if isinstance(condition, str):
                    where_conditions.append(condition)
                else:
                    where_conditions.append(str(condition))
            sql += " WHERE " + " AND ".join(where_conditions)

        if query._order_by and not count and not delete:
            order_clauses = [f"{field} {dir}" for field, dir in query._order_by]
            sql += " ORDER BY " + ", ".join(order_clauses)

        if query._limit is not None and not count and not delete:
            sql += f" LIMIT {query._limit}"

        if query._offset is not None and not count and not delete:
            sql += f" OFFSET {query._offset}"

        return sql, params