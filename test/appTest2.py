# test/appTest.py
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import editedapp3 as task3


@pytest.fixture()
def client():
    task3.app.config["TESTING"] = True
    with task3.app.test_client() as c:
        yield c


# ---------------- CPU ----------------

def test_cpu_current_reads_psutil(client, monkeypatch):
    # Your app uses psutil, not in-memory lists -> mock psutil
    monkeypatch.setattr("editedapp3.psutil.cpu_percent", lambda interval=None: 30.2)
    resp = client.get("/cpu/current")
    assert resp.status_code == 200
    data = resp.get_json()
    # Your app already returns this key; just assert the mocked value
    assert "cpu current usage percent" in data
    assert data["cpu current usage percent"] == 30.2


def test_cpu_avg24h_uses_db_empty_returns_list(client, monkeypatch):
    # Mock DB connector to return no rows
    class FakeCur:
        def execute(self, *a, **k): pass
        def fetchall(self): return []  # empty
        def close(self): pass
    class FakeConn:
        def cursor(self): return FakeCur()
        def close(self): pass
    monkeypatch.setattr("editedapp3.pymysql.connect", lambda **kw: FakeConn())

    resp = client.get("/cpu/avg24h")
    assert resp.status_code == 200
    data = resp.get_json()
    # Your app returns "... newest to oldest"
    key = "cpu avg usage percent for the last 24 hours newest to oldest"
    assert key in data
    assert data[key] == []


def test_cpu_avg24h_uses_db_values(client, monkeypatch):
    # Return two hourly rows; assert they show up
    rows = [("2025-08-26 10:00", 10.0), ("2025-08-26 11:00", 50.0)]
    class FakeCur:
        def execute(self, *a, **k): pass
        def fetchall(self): return rows
        def close(self): pass
    class FakeConn:
        def cursor(self): return FakeCur()
        def close(self): pass
    monkeypatch.setattr("editedapp3.pymysql.connect", lambda **kw: FakeConn())

    resp = client.get("/cpu/avg24h")
    assert resp.status_code == 200
    data = resp.get_json()
    key = "cpu avg usage percent for the last 24 hours newest to oldest"
    assert key in data
    vals = data[key]
    assert isinstance(vals, list)
    # order may be newest->oldest; just check presence
    assert any(abs(v - 10.0) < 1e-6 for v in vals)
    assert any(abs(v - 50.0) < 1e-6 for v in vals)


# ---------------- MEM ----------------

def test_mem_current_reads_psutil(client, monkeypatch):
    class VM: percent = 120.0
    monkeypatch.setattr("editedapp3.psutil.virtual_memory", lambda: VM())
    resp = client.get("/mem/current")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "mem current usage percent" in data
    assert data["mem current usage percent"] == 120.0


def test_mem_avg24h_uses_db(client, monkeypatch):
    rows = [("2025-08-26 10:00", 70.0), ("2025-08-26 11:00", 120.0)]
    class FakeCur:
        def execute(self, *a, **k): pass
        def fetchall(self): return rows
        def close(self): pass
    class FakeConn:
        def cursor(self): return FakeCur()
        def close(self): pass
    monkeypatch.setattr("editedapp3.pymysql.connect", lambda **kw: FakeConn())

    resp = client.get("/mem/avg24h")
    assert resp.status_code == 200
    data = resp.get_json()
    key = "mem avg usage percent for the last 24 hours newest to oldest"
    assert key in data
    vals = data[key]
    assert any(abs(v - 70.0) < 1e-6 for v in vals)
    assert any(abs(v - 120.0) < 1e-6 for v in vals)


# ---------------- DISK ----------------

def test_disk_current_reads_psutil(client, monkeypatch):
    class DU: percent = 30.2
    monkeypatch.setattr("editedapp3.psutil.disk_usage", lambda path="/": DU())
    resp = client.get("/disk/current")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "disk current usage percent" in data
    assert data["disk current usage percent"] == 30.2


def test_disk_avg24h_uses_db(client, monkeypatch):
    rows = [("2025-08-26 10:00", 10.0), ("2025-08-26 11:00", 50.0)]
    class FakeCur:
        def execute(self, *a, **k): pass
        def fetchall(self): return rows
        def close(self): pass
    class FakeConn:
        def cursor(self): return FakeCur()
        def close(self): pass
    monkeypatch.setattr("editedapp3.pymysql.connect", lambda **kw: FakeConn())

    resp = client.get("/disk/avg24h")
    assert resp.status_code == 200
    data = resp.get_json()
    key = "disk avg usage percent for the last 24 hours newest to oldest"
    assert key in data
    vals = data[key]
    assert any(abs(v - 10.0) < 1e-6 for v in vals)
    assert any(abs(v - 50.0) < 1e-6 for v in vals)

