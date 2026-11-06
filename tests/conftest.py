import os
import socket
import subprocess
import sys
import time

import pytest
import redis

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def redis_server(tmp_path_factory):
    """Start a throwaway redis-server for the test session."""
    port = _free_port()
    proc = subprocess.Popen(
        ["redis-server", "--port", str(port), "--save", "", "--appendonly", "no",
         "--dir", str(tmp_path_factory.mktemp("redis"))],
        stdout=subprocess.DEVNULL,
    )
    client = redis.Redis(port=port, decode_responses=True)
    for _ in range(50):
        try:
            client.ping()
            break
        except redis.ConnectionError:
            time.sleep(0.1)
    os.environ["REDIS_PORT"] = str(port)
    yield port
    proc.terminate()
    proc.wait()


@pytest.fixture
def r(redis_server):
    client = redis.Redis(port=redis_server, decode_responses=True)
    client.flushall()
    return client
