from bookkeeper.repository.abstract_repository import AbstractRepository, T, Any
import sqlite3
from inspect import get_annotations

class SQLiteRepository(AbstractRepository[T]):
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
        p = ', '.join("?" * len(self.fields))
        values = [getattr(obj, x) for x in self.fields]
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute('PRAGMA foreign_keys = ON')
            cur.execute(
                f'INSERT INTO {self.table_name} ({names}) VALUES({p})',
                values
            )
            obj.pk = cur.lastrowid
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
            obj = self.cls(pk=pk, **dict(zip(self.fields, row)))
            return obj
        else:
            return None

    def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            if where:
                fields = " AND ".join([f"{k}={repr(v)}" for k,v in where.items()])
                rows = cur.execute(
                    f'SELECT ROWID, * FROM {self.table_name} '
                    + f'WHERE {fields}'
                ).fetchall()
                print(fields,rows)

                
            else:
                rows = cur.execute(
                    f'SELECT ROWID, * FROM {self.table_name} '
                ).fetchall()
                
        con.close()
        return [self.cls(pk=r[0], **dict(zip(self.fields, r[1:]))) for r in rows]

    def update(self, obj: T) -> None:
        pass

    def delete(self, pk: int) -> None:
        pass
