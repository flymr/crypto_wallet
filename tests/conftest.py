from typing import Type
import pytest
from eth_tester import (
    EthereumTester,
    PyEVMBackend
)
from eth_utils import to_wei
from web3 import (
    EthereumTesterProvider,
    Web3,
)
from hexbytes import HexBytes
from rest_framework.test import APIClient
import crypto_wallet.nodes
from crypto_wallet.nodes import Node
from crypto_wallet.constants import CURRENCIES
from crypto_wallet.wallet.models import Wallet


@pytest.fixture
def start_ether_balance() -> int:
    return to_wei(1, 'ether')


@pytest.fixture
def num_of_rich_accounts() -> int:
    return 2


@pytest.fixture
def pyevm_backend(start_ether_balance, num_of_rich_accounts) -> PyEVMBackend:
    custom_genesis_state = PyEVMBackend._generate_genesis_state(
        overrides=dict(balance=start_ether_balance),
        num_accounts=num_of_rich_accounts
    )
    return PyEVMBackend(genesis_state=custom_genesis_state)


@pytest.fixture
def eth_tester(pyevm_backend) -> EthereumTester:
    return EthereumTester(backend=pyevm_backend)


@pytest.fixture
def eth_tester_provider(eth_tester) -> EthereumTesterProvider:
    return EthereumTesterProvider(ethereum_tester=eth_tester)


@pytest.fixture
def w3(eth_tester_provider) -> Web3:
    return Web3(eth_tester_provider)


@pytest.fixture
def eth_node(w3) -> Node:
    crypto_wallet.nodes.nodes[CURRENCIES.ETH].client = w3
    return crypto_wallet.nodes.nodes[CURRENCIES.ETH]


@pytest.fixture
def eth_accounts_with_balance(eth_tester):
    return list(zip(eth_tester.get_accounts(), eth_tester.backend.account_keys))


@pytest.fixture
def eth_rich_address(eth_accounts_with_balance) -> HexBytes:
    address, _ = eth_accounts_with_balance[0]
    return address


@pytest.fixture
def api_client() -> Type[APIClient]:
    return APIClient


@pytest.fixture
def eth_internal_wallet(eth_node) -> Wallet:
    address, private_key = eth_node.create_address()
    obj = Wallet.objects.create(
        currency=eth_node.currency,
        address=address,
        private_key=private_key,
    )
    return obj
