from datetime import datetime

import pytest
from bookkeeper.repository.memory_repository import MemoryRepository
from bookkeeper.models.budget import Budget


@pytest.fixture
def repo():
    return MemoryRepository()


def test_create_with_full_args_list():
    b = Budget(amount=1000, category=1, period=7, pk=1)
    assert b.amount == 1000
    assert b.category == 1


def test_create_brief():
    b = Budget(1000, 1, 2)
    assert b.amount == 1000
    assert b.category == 1


def test_can_add_to_repo(repo):
    b = Budget(1000, 1, 2)
    pk = repo.add(b)
    assert b.pk == pk
