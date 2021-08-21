from crypto_wallet.constants import CURRENCIES
from crypto_wallet.nodes import nodes


def test_nodes():
    assert all(nodes.values())
    assert set(CURRENCIES.KEYS) == set(nodes.keys())
