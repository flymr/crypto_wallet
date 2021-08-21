from hexbytes import HexBytes
from web3 import Web3
from crypto_wallet.constants import CURRENCIES


class TestEthereumNode:

    def test_check_address(self, eth_node, eth_accounts_with_balance) -> None:
        address, private_key = eth_accounts_with_balance[0]
        assert eth_node.check_address(address)
        assert not eth_node.check_address('invalid_value')
        assert not eth_node.check_address(private_key)

    def test_create_private_key(self, eth_node) -> None:
        private_key = eth_node.create_private_key()
        assert HexBytes(private_key)

    def test_address_nonce(self, eth_node, eth_rich_address) -> None:
        assert eth_node.address_nonce(eth_rich_address) == 0

    def test_address_balance(self, eth_node, eth_rich_address, start_ether_balance):
        assert eth_node.address_balance(eth_rich_address) == start_ether_balance

    def test_create_ethereum_address(self, eth_node) -> None:
        private_key = eth_node.create_private_key()
        address, _ = eth_node.create_address()
        assert HexBytes(private_key)
        assert eth_node.check_address(address)

    def test_transfer_to_address(self, eth_node, eth_accounts_with_balance) -> None:
        address1, private_key = eth_accounts_with_balance[0]
        address2, _ = eth_accounts_with_balance[1]
        balance_from = eth_node.address_balance(address2)
        balance_to = eth_node.address_balance(address1)
        nonce, tx_hash = eth_node.transfer_to_address(
            private_key=private_key,
            address_from=address1,
            address_to=address2
        )
        assert eth_node.address_balance(address1) == 0
        assert eth_node.address_balance(address2) == balance_from + balance_to - eth_node.total_commission
        assert nonce == 1

    def test_property_client(self, eth_node):
        assert type(eth_node.client) is Web3

    def test_property_gas(self, eth_node):
        assert type(eth_node.gas) is int

    def test_property_gas_price(self, eth_node):
        assert type(eth_node.gas_price) is int

    def test_property_currency(self, eth_node):
        assert eth_node.currency == CURRENCIES.ETH
