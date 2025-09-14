import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from collections import deque
from datetime import datetime, timedelta
import editedapp3 as task3


@pytest.fixture()
def client():
    task3.app.config["TESTING"] = True
    with task3.app.test_client() as client:
        yield client


def test_cpu_current_no_samples(client):
    resp = client.get("/cpu/current")
    assert resp.status_code ==200
    assert resp.get_json()["error"]=="no samples yet"


def test_cpu_current_with_samples(client, monkeypatch):
    monkeypatch.setattr(task3, "cpuValues", [10.0,20.5,30.2])
    resp = client.get("/cpu/current")
    data = resp.get_json()
    assert "cpu current usage percent" in data
    assert data["cpu current usage percent"]==30.2


def test_cpu_avg24h_no_samples(client, monkeypatch):
    monkeypatch.setattr(task3, "cpuValues",[])
    resp = client.get("/cpu/avg24h")
    data = resp.get_json()
    assert "error" in data


def test_cpu_avg24h_with_samples(client, monkeypatch):
    samples = [10.0]*3600 +[50.0] *3600
    monkeypatch.setattr(task3, "cpuValues", samples)
    resp = client.get("/cpu/avg24h")
    data = resp.get_json()
    assert "cpu avg usage percent for the last 24 hours" in data
    values = data["cpu avg usage percent for the last 24 hours"]
    assert isinstance(values, list)
    assert len(values) >= 2 
    assert any(abs(v -10.0) < 0.1 for v in values if v is not None)
    assert any(abs(v -50.0) < 0.1 for v in values if v is not None)



def test_mem_current_no_samples(client):
    resp = client.get("/mem/current")
    assert resp.status_code == 200
    assert resp.get_json()["error"]=="no samples yet"



def test_mem_current_with_samples(client, monkeypatch):
    monkeypatch.setattr(task3, "memValues", [70.2 , 75.4,120])
    resp = client.get("/mem/current")
    data = resp.get_json()
    assert "mem current usage percent" in data
    assert data["mem current usage percent"]==120



def test_mem_avg24h_no_samples(client, monkeypatch):
    monkeypatch.setattr(task3, "memValues",[])
    resp = client.get("/mem/avg24h")
    data = resp.get_json()
    assert "error" in data

def test_mem_avg24h_with_samples(client, monkeypatch):
    samples = [70.0]*3600 +[120.0]*3600
    monkeypatch.setattr(task3, "memValues", samples)
    resp = client.get("/mem/avg24h")
    data = resp.get_json()
    assert "mem avg usage percent for the last 24 hours" in data
    values = data["mem avg usage percent for the last 24 hours"]
    assert isinstance(values, list)
    assert len(values)>= 2  
    assert any(abs(v-70.0) < 0.1 for v in values if v is not None)
    assert any(abs(v-120.0) < 0.1 for v in values if v is not None)


def test_disk_current_no_samples(client):
    resp = client.get("/disk/current")
    assert resp.status_code==200
    assert resp.get_json()["error"]=="no samples yet"


def test_disk_current_with_samples(client, monkeypatch):
    monkeypatch.setattr(task3, "diskValues", [10.0,20.5,30.2])
    resp = client.get("/disk/current")
    data = resp.get_json()
    assert "disk current usage percent" in data
    assert data["disk current usage percent"]==30.2


def test_disk_avg24h_no_samples(client, monkeypatch):
    monkeypatch.setattr(task3, "diskValues",[])
    resp = client.get("/disk/avg24h")
    data = resp.get_json()
    assert "error" in data


def test_dsik_avg24h_with_samples(client, monkeypatch):
    samples = [10.0]*3600 +[50.0] *3600
    monkeypatch.setattr(task3, "diskValues", samples)
    resp = client.get("/disk/avg24h")
    data = resp.get_json()
    assert "disk avg usage percent for the last 24 hours" in data
    values = data["disk avg usage percent for the last 24 hours"]
    assert isinstance(values, list)
    assert len(values)>=2 
    assert any(abs(v-10.0) <0.1 for v in values if v is not None)
    assert any(abs(v-50.0) <0.1 for v in values if v is not None)

