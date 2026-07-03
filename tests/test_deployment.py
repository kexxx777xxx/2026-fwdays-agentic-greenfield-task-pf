"""@trace FR-052 — docker compose brings up app + a separate ephemeral qdrant.

Unit: asserts the compose topology (TC-004, TC-005, TC-006) statically.
"""

from pathlib import Path

import yaml

COMPOSE = Path(__file__).resolve().parents[1] / "docker-compose.yaml"


def _services():
    return yaml.safe_load(COMPOSE.read_text(encoding="utf-8"))["services"]


def test_app_and_qdrant_are_separate_services():
    services = _services()
    assert "app" in services
    assert "qdrant" in services  # vector store is its own service (TC-005)


def test_app_depends_on_qdrant():
    app = _services()["app"]
    assert "qdrant" in app.get("depends_on", [])
    assert "build" in app  # app image is built locally


def test_qdrant_has_no_named_volume():
    # Ephemeral store so idempotency tests start clean (TC-006).
    qdrant = _services()["qdrant"]
    assert not qdrant.get("volumes")
