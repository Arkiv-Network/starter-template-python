import json
import re

from explorer import cli  # type: ignore[import-untyped]


def test_entity_shows_metadata(arkiv_client, capsys, monkeypatch):
    # Create entity
    entity_key, receipt = arkiv_client.arkiv.create_entity(
        payload=b"{\"msg\": \"hello\"}",
        content_type="application/json",
        expires_in=arkiv_client.arkiv.to_seconds(days=1),
        attributes={"type": "test"},
    )

    # Patch connect to return the fixture client
    monkeypatch.setattr(cli, "_connect_client", lambda: arkiv_client)

    # Run the CLI main for the entity
    rc = cli.main(["entity", entity_key])
    assert rc == 0

    captured = capsys.readouterr()
    out = captured.out.strip()
    # Should be valid JSON
    data = json.loads(out)

    assert data["$key"] == entity_key
    assert data["attributes"]["type"] == "test"
    assert data["payload"]["msg"] == "hello"


def test_entity_not_found(arkiv_client, capsys, monkeypatch):
    monkeypatch.setattr(cli, "_connect_client", lambda: arkiv_client)

    rc = cli.main(["entity", "0xdeadbeef"])  # nonexistent
    assert rc == 2

    captured = capsys.readouterr()
    assert "Entity not found" in captured.err
