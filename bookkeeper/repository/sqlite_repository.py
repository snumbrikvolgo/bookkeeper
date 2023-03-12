"""
Модуль описывает репозиторий, работающий с БД на компьютере
"""

import sqlite3
from typing import Any
from inspect import get_annotations
from bookkeeper.repository.abstract_repository import AbstractRepository, T


class SQLiteRepository(AbstractRepository[T]):
    """
    Репозиторий, работающий с базой данных на компьютере.
    """
    db_file: str
    table_name: str
    fields: dict[str, Any]
    cls: type

    def __init__(self, db_file: str, cls: type) -> None:
        self.db_file = db_file
        self.table_name = cls.__name__.lower()
        self.fields = get_annotations(cls, eval_str=True)
        self.fields.pop('pk')
        self.cls = cls

    def add(self, obj: T) -> int:
        if getattr(obj, 'pk', None) != 0:
            raise ValueError(f'trying to add object {obj} with filled `pk` attribute')
        names = ', '.join(self.fields.keys())
        unknown_values = ', '.join("?" * len(self.fields))
        values = [getattr(obj, x) for x in self.fields]
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute('PRAGMA foreign_keys = ON')
            cur.execute(
                f'INSERT INTO {self.table_name} ({names}) VALUES({unknown_values})',
                values
            )
            if cur.lastrowid is not None:
                obj.pk = cur.lastrowid
            # else:
            #     raise ValueError(f'Unable to add {obj}')
        con.close()
        return obj.pk

    def get(self, pk: int) -> T | None:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            row = cur.execute(
                f'SELECT * FROM {self.table_name} '
                + f'WHERE ROWID=={pk}'
            ).fetchone()
        con.close()
        if row:
            obj: T = self.cls(pk=pk, **dict(zip(self.fields, row)))
            return obj
        return None

    def get_all(self, where: dict[str, Any] | None = None,
                operator: str = "=") -> list[T]:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            if where:
                fields = " AND ".join([f"{k} {operator} {repr(v)}"
                                       for k, v in where.items()])
                rows = cur.execute(
                    f'SELECT ROWID, * FROM {self.table_name} '
                    + f'WHERE {fields}'
                ).fetchall()
            else:
                rows = cur.execute(
                    f'SELECT ROWID, * FROM {self.table_name} '
                ).fetchall()
        con.close()
        return [self.cls(pk=r[0], **dict(zip(self.fields, r[1:]))) for r in rows]

    def get_all_like(self, like: dict[str, str]) -> list[T]:
        values = [f"%{v}%" for v in like.values()]
        where = dict(zip(like.keys(), values))
        return self.get_all(where=where, operator='LIKE')

    def update(self, obj: T) -> None:
        fields = ", ".join([f"{x}=?" for x in self.fields.keys()])
        values = [getattr(obj, x) for x in self.fields]
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(
                f'UPDATE {self.table_name} SET {fields} '
                + f'WHERE ROWID=={obj.pk}',
                values
            )
            if cur.rowcount == 0:
                raise ValueError('attempt to update object with unknown primary key')

        con.close()

    def delete(self, pk: int) -> None:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(
                f'DELETE FROM  {self.table_name} '
                + f'WHERE ROWID=={pk}'
            )
            if cur.rowcount == 0:
                raise ValueError('attempt to delete object with unknown primary key')
        con.close()
