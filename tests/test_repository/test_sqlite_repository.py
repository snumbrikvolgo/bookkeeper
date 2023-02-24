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

def test_get_getall(repo, custom_class):
    obj = custom_class(f1=0, f2="test_get")
    repo.add(obj)
    assert repo.get_all() == [obj] 
    assert repo.get(1) == obj
    assert [repo.get(1)] == repo.get_all()


def test_update(repo, custom_class):
    objects1 = [custom_class(f1=int(i)) for i in range(5)]
    for o in objects1:
        repo.add(o)
    assert repo.get_all() == objects1

    obj_upd = custom_class(f1=0, f2="test_update", pk=3)
    repo.update(obj_upd)
    obj_get = repo.get(3)
    assert repo.get_all() != objects1

    assert obj_get.pk == obj_upd.pk
    assert obj_get.f1 == obj_upd.f1
    assert obj_get.f2 == obj_upd.f2


def test_update(repo, custom_class):
    objects1 = [custom_class(f1=int(i)) for i in range(5)]
    for o in objects1:
        repo.add(o)
    assert repo.get_all() == objects1

    obj_upd = custom_class(f1=0, f2="test_update", pk=3)
    repo.update(obj_upd)
    obj_get = repo.get(3)
    assert repo.get_all() != objects1

    assert obj_get.pk == obj_upd.pk
    assert obj_get.f1 == obj_upd.f1
    assert obj_get.f2 == obj_upd.f2


def test_update_unexcistence(repo, custom_class):
    objects1 = [custom_class(f1=int(i)) for i in range(5)]
    for o in objects1:
        repo.add(o)
    assert repo.get_all() == objects1

    obj_upd = custom_class(f1=0, f2="test_update", pk=10)
    with pytest.raises(ValueError):
        repo.update(obj_upd)

def test_update_no_pk(repo, custom_class):
    objects1 = [custom_class(f1=int(i)) for i in range(5)]
    for o in objects1:
        repo.add(o)
    assert repo.get_all() == objects1

    obj_upd = custom_class(f1=0, f2="test_update")
    with pytest.raises(ValueError):
        repo.update(obj_upd)

def test_delete_one(repo, custom_class):
    obj=custom_class(f1=10, f2='kek')
    repo.add(obj)
    assert repo.get_all() == [obj]
    repo.delete(obj.pk)
    assert repo.get_all() == []


def test_delete_middle(repo, custom_class):
    objects1 = [custom_class(f1=int(i)) for i in range(5)]
    for o in objects1:
        repo.add(o)
    assert repo.get_all() == objects1
    repo.delete(objects1[2].pk)
    objects1.pop(2)
    assert repo.get_all() == objects1

def test_crud(repo, custom_class):
    obj = custom_class()
    pk = repo.add(obj)
    assert obj.pk == pk
    assert repo.get(pk) == obj
    obj2 = custom_class()
    obj2.pk = pk
    repo.update(obj2)
    assert repo.get(pk) == obj2
    repo.delete(pk)
    assert repo.get(pk) is None
