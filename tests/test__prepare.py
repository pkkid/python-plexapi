# -*- coding: utf-8 -*-
import time

import pytest

MAX_ATTEMPTS = 60


def wait_for_idle_server(server):
    """Wait for PMS activities to complete with a timeout."""
    attempts = 0
    while server.activities and attempts < MAX_ATTEMPTS:
        print(f"Watiing for activities to finish: {server.activities}")
        time.sleep(1)
        attempts += 1
    assert attempts < MAX_ATTEMPTS, f"Server still busy after {MAX_ATTEMPTS}s"


def test_ensure_metadata_scans_completed(plex):
    wait_for_idle_server(plex)


@pytest.mark.authenticated
def test_ensure_metadata_scans_completed_authenticated(plex):
    wait_for_idle_server(plex)
