from bookkeeper.repository.sqlite_repository import SQLiteRepository
import sqlite3
from dataclasses import dataclass

import pytest


DB_FILE = "database/test_sqlrepo.db"

@pytest.fixture
def create_database():
    with sqlite3.connect(DB_FILE) as con:
        cur = con.cursor()
        cur.execute(f"DROP TABLE custom")
    with sqlite3.connect(DB_FILE) as con:
        cur = con.cursor()
        cur.execute(f"CREATE TABLE custom(f1, f2)")
    con.close()



@pytest.fixture
def custom_class():
    @dataclass
    class Custom():
        pk: int = 0
        f1: int = 10
        f2: str = 'cat'
    return Custom


@pytest.fixture
def repo(custom_class, create_database):
    return SQLiteRepository(
        db_file='database/test_sqlrepo.db',\
        cls=custom_class
    )

def test_cannot_add_with_pk(repo, custom_class):
    obj = custom_class(pk=5)
    print(obj)
    with pytest.raises(ValueError):
        repo.add(obj)


def test_cannot_add_without_pk(repo):
    with pytest.raises(ValueError):
        repo.add(0)

def test_get_all(repo, custom_class):
    objects1 = [custom_class(f1=int(i), f2='test2') for i in range(5)]
    for o in objects1:
        repo.add(o)
    assert repo.get_all() == objects1

    objects2 = [custom_class(f1=int(i)) for i in range(5)]
    for o in objects2:
        repo.add(o)
    assert repo.get_all() == objects1 + objects2

    objects3 = [custom_class() for i in range(5)]
    for o in objects3:
        repo.add(o)
    assert repo.get_all() == objects1 + objects2 + objects3

def test_get_all_with_condition(repo, custom_class):
    objects = []
    for i in range(5):
        o = custom_class()
        o.f1 = 16
        o.f2 = str(i)
        repo.add(o)
        objects.append(o)
    for i in range(5):
        assert repo.get_all({'f2': str(i)}) == [objects[i]]
    assert repo.get_all({'f1': 16}) == objects

