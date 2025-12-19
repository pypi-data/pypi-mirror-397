import logging
import socket
import threading
import time
from importlib import metadata

import pytest

import popoto_api.popoto as popoto_module
from popoto_data_server.pds import run_server


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _wait_for_port(host: str, port: int, timeout: float = 5.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.2):
                return
        except OSError:
            time.sleep(0.05)
    raise TimeoutError(f"Port {port} on {host} did not open within {timeout} seconds")


@pytest.fixture(scope="module")
def data_server():
    """Start the data server on an open port for integration testing."""
    original_port = popoto_module.VERSION_SERVER_PORT
    try:
        port = _find_free_port()
    except PermissionError:
        pytest.skip("Socket operations not permitted in this environment")
    popoto_module.VERSION_SERVER_PORT = port
    server_thread = threading.Thread(
        target=run_server, kwargs={"port": port}, daemon=True
    )
    server_thread.start()
    _wait_for_port("127.0.0.1", port)
    yield
    popoto_module.VERSION_SERVER_PORT = original_port


def test_get_version_returns_popoto_api_version(data_server):
    popoto_version = metadata.version("popoto-api")

    # Bypass heavy popoto __init__ that expects modem connectivity.
    client = popoto_module.popoto.__new__(popoto_module.popoto)
    client.ip = "127.0.0.1"
    client.logger = logging.getLogger("test-popoto")

    versions = client.getVersion()
    print(f"versions from data server: {versions}")
    print(versions)

    assert isinstance(versions, list)
    assert any(
        isinstance(entry, dict) and entry.get("popoto-api") == popoto_version
        for entry in versions
    ), f"popoto-api version not found in {versions}"
