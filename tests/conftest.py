"""Test configuration for starter template examples."""

import pytest

from arkiv import Arkiv, NamedAccount
from arkiv.node import ArkivNode
from arkiv.provider import ProviderBuilder


@pytest.fixture(scope="session")
def arkiv_node():
    """Provide a running Arkiv node for tests."""
    node = ArkivNode()
    node.start()
    yield node
    node.stop()


@pytest.fixture(scope="session")
def arkiv_client(arkiv_node: ArkivNode):
    """Provide an Arkiv client connected to test node."""
    provider = ProviderBuilder().node(arkiv_node).build()

    # Create and fund test account
    account = NamedAccount.create("test-account")
    arkiv_node.fund_account(account)
    
    client = Arkiv(provider, account=account)

    return client


@pytest.fixture
def test_payload():
    """Provide test payload data."""
    return b"Test entity for automated testing"


@pytest.fixture
def test_attributes():
    """Provide test attributes."""
    return {"type": "test", "purpose": "automation", "version": 1}
