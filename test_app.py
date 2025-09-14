import pytest
from unittest.mock import MagicMock, patch
from editedapp3 import app  
@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()

@patch("editedapp3.get_conn")
def test_cpu_current_with_sample(mock_get_conn, client):
    cur = MagicMock()
    cur.fetchone.return_value=(22.2,"2025-08-27T19:10:02+00:00")
    conn=MagicMock()
    conn.cursor.return_value.__enter__.return_value = cur
    mock_get_conn.return_value = conn
    res = client.get("/cpu/current")
    assert res.status_code==200
    assert res.get_json()["cpu current usage percent"]==22.2

@patch("editedapp3.get_conn")
def test_cpu_current_no_sample(mock_get_conn, client):
    cur=MagicMock()
    cur.fetchone.return_value=None
    conn=MagicMock()
    conn.cursor.return_value.__enter__.return_value = cur
    mock_get_conn.return_value = conn
    res = client.get("/cpu/current")
    assert res.status_code == 404


@patch("editedapp3.get_conn")
def test_cpu_avg24h_with_samples(mock_get_conn, client):
    samples=[(i,) for i in range(1440)]
    cur=MagicMock()
    cur.fetchall.return_value=samples
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cur
    mock_get_conn.return_value = conn

    res = client.get("/cpu/avg24h")
    data = res.get_json()
    assert res.status_code ==200
    assert len(data["cpu avg usage percent for the last 24 hours newest to oldest"]) ==24

@patch("editedapp3.get_conn")
def test_cpu_avg24h_no_samples(mock_get_conn, client):
    cur = MagicMock()
    cur.fetchall.return_value=[]
    conn=MagicMock()
    conn.cursor.return_value.__enter__.return_value = cur
    mock_get_conn.return_value = conn
    res = client.get("/cpu/avg24h")
    assert res.status_code==404


@patch("editedapp3.get_conn")
def test_mem_current_with_sample(mock_get_conn, client):
    cur = MagicMock()
    cur.fetchone.return_value = (53.3, "2025-08-27T19:17:01+00:00")
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cur
    mock_get_conn.return_value = conn
    res = client.get("/mem/current")
    assert res.status_code == 200
    assert res.get_json()["mem current usage percent"] == 53.3


@patch("editedapp3.get_conn")
def test_mem_current_no_sample(mock_get_conn, client):
    cur = MagicMock()
    cur.fetchone.return_value = None
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cur
    mock_get_conn.return_value = conn

    res = client.get("/mem/current")
    assert res.status_code == 404


@patch("editedapp3.get_conn")
def test_mem_avg24h_with_samples(mock_get_conn, client):
    samples = [(i,) for i in range(1440)]
    cur = MagicMock()
    cur.fetchall.return_value = samples
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cur
    mock_get_conn.return_value = conn

    res = client.get("/mem/avg24h")
    data = res.get_json()
    assert res.status_code == 200
    assert len(data["mem avg usage percent for the last 24 hours newest to oldest"]) == 24


@patch("editedapp3.get_conn")
def test_mem_avg24h_no_samples(mock_get_conn, client):
    cur = MagicMock()
    cur.fetchall.return_value=[]
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cur
    mock_get_conn.return_value = conn

    res = client.get("/mem/avg24h")
    assert res.status_code == 404


@patch("editedapp3.get_conn")
def test_disk_current_with_sample(mock_get_conn, client):
    cur = MagicMock()
    cur.fetchone.return_value = (86.7, "2025-08-27T19:17:01+00:00")
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cur
    mock_get_conn.return_value = conn

    res = client.get("/disk/current")
    assert res.status_code == 200
    assert res.get_json()["disk current usage percent"] == 86.7


@patch("editedapp3.get_conn")
def test_disk_current_no_sample(mock_get_conn, client):
    cur = MagicMock()
    cur.fetchone.return_value = None
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cur
    mock_get_conn.return_value = conn

    res = client.get("/disk/current")
    assert res.status_code == 404


@patch("editedapp3.get_conn")
def test_disk_avg24h_with_samples(mock_get_conn, client):
    samples = [(i,) for i in range(1440)]
    cur = MagicMock()
    cur.fetchall.return_value = samples
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cur
    mock_get_conn.return_value = conn

    res = client.get("/disk/avg24h")
    data = res.get_json()
    assert res.status_code == 200
    assert len(data["disk avg usage percent for the last 24 hours newest to oldest"]) == 24


@patch("editedapp3.get_conn")
def test_disk_avg24h_no_samples(mock_get_conn, client):
    cur = MagicMock()
    cur.fetchall.return_value = []
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cur
    mock_get_conn.return_value = conn
    res = client.get("/disk/avg24h")
    assert res.status_code == 404

