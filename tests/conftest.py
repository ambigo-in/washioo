import os
import uuid
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest


os.environ.setdefault("DATABASE_URL", "sqlite:///./test_probe.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-value-with-more-than-32-characters")
os.environ.setdefault("RATE_LIMIT_ENABLED", "False")
os.environ.setdefault("WEB_PUSH_ENABLED", "False")
os.environ.setdefault("SUPABASE_STORAGE_BUCKET", "test-bucket")


def obj(**kwargs):
    return SimpleNamespace(**kwargs)


def uid():
    return uuid.uuid4()


class FakeQuery:
    def __init__(
        self,
        first_result=None,
        all_result=None,
        count_result=0,
        one_result=None,
        scalar_result=0,
        delete_result=0,
    ):
        self.first_result = first_result
        self.all_result = [] if all_result is None else all_result
        self.count_result = count_result
        self.one_result = one_result
        self.scalar_result = scalar_result
        self.delete_result = delete_result
        self.updated = None
        self.calls = []

    def _chain(self, name, *args, **kwargs):
        self.calls.append((name, args, kwargs))
        return self

    def filter(self, *args, **kwargs):
        return self._chain("filter", *args, **kwargs)

    def options(self, *args, **kwargs):
        return self._chain("options", *args, **kwargs)

    def order_by(self, *args, **kwargs):
        return self._chain("order_by", *args, **kwargs)

    def offset(self, *args, **kwargs):
        return self._chain("offset", *args, **kwargs)

    def limit(self, *args, **kwargs):
        return self._chain("limit", *args, **kwargs)

    def join(self, *args, **kwargs):
        return self._chain("join", *args, **kwargs)

    def with_for_update(self, *args, **kwargs):
        return self._chain("with_for_update", *args, **kwargs)

    def first(self):
        return self.first_result

    def all(self):
        return self.all_result

    def count(self):
        return self.count_result

    def one(self):
        return self.one_result

    def scalar(self):
        return self.scalar_result

    def update(self, data, **kwargs):
        self.updated = data
        if self.first_result:
            for key, value in data.items():
                setattr(self.first_result, key, value)
        return self.count_result or 1

    def delete(self, **kwargs):
        return self.delete_result


class FakeDB:
    def __init__(self, queries=None):
        self.queries = list(queries or [])
        self.added = []
        self.deleted = []
        self.commits = 0
        self.rollbacks = 0
        self.flushes = 0
        self.refreshed = []
        self.closed = False
        self.query_models = []

    def query(self, *models):
        self.query_models.append(models)
        if self.queries:
            return self.queries.pop(0)
        return FakeQuery()

    def add(self, value):
        self.added.append(value)

    def delete(self, value):
        self.deleted.append(value)

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def flush(self):
        self.flushes += 1

    def refresh(self, value):
        self.refreshed.append(value)

    def close(self):
        self.closed = True


@pytest.fixture
def fake_db():
    return FakeDB()


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def now():
    return datetime(2026, 1, 2, 3, 4, 5)


@pytest.fixture
def future_datetime():
    return datetime.utcnow() + timedelta(days=1)


@pytest.fixture(autouse=True)
def block_external_services(monkeypatch):
    monkeypatch.setattr(
        "services.realtime_service.emit_user_event",
        lambda *args, **kwargs: None,
        raising=False,
    )
    monkeypatch.setattr(
        "services.realtime_service.emit_role_event",
        lambda *args, **kwargs: None,
        raising=False,
    )
