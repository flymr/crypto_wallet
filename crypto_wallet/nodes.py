import secrets
from typing import Tuple, Any

from hexbytes import HexBytes
from web3 import Web3
from django.conf import settings
from abc import ABC, ABCMeta, abstractmethod

from crypto_wallet.constants import CURRENCIES


class SingletonMeta(ABCMeta):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Node(ABC):

    @property
    @abstractmethod
    def client(self) -> Any: pass

    @property
    @abstractmethod
    def gas_price(self) -> int: pass

    @property
    @abstractmethod
    def gas(self) -> int: pass

    @property
    @abstractmethod
    def currency(self) -> str: pass

    @property
    @abstractmethod
    def total_commission(self) -> int: pass

    @abstractmethod
    def create_address(self, private_key: HexBytes = None) -> Tuple[HexBytes, HexBytes]: pass

    @abstractmethod
    def transfer_to_address(
            self, private_key: HexBytes,
            address_from: HexBytes,
            address_to: HexBytes,
            value: float = None,
            wait_until_complete: bool = True
    ) -> Tuple[int, HexBytes]: pass

    @abstractmethod
    def address_balance(self, address: HexBytes) -> int: pass

    @abstractmethod
    def address_nonce(self, address: HexBytes) -> int: pass

    @abstractmethod
    def create_private_key(self) -> HexBytes: pass

    @abstractmethod
    def check_address(self, address: HexBytes) -> bool: pass


class EthereumNode(Node, metaclass=SingletonMeta):
    _client = Web3(Web3.HTTPProvider(settings.ETH_INFURA_URL))
    _gas = int(settings.ETH_GAS)

    @property
    def client(self) -> Web3:
        return self._client

    @client.setter
    def client(self, value):
        self._client = value

    @property
    def gas_price(self) -> int:
        return self.client.eth.gas_price

    @property
    def gas(self) -> int:
        return self._gas

    @property
    def total_commission(self) -> int:
        return self.gas * self.gas_price

    @property
    def currency(self):
        return CURRENCIES.ETH

    def create_address(self, privat_key: HexBytes = None) -> Tuple[HexBytes, HexBytes]:
        if privat_key is None:
            privat_key = self.create_private_key()
        acc = self.client.eth.account.from_key(privat_key)
        address = acc.address
        return address, privat_key

    def transfer_to_address(self, private_key: HexBytes, address_from: HexBytes, address_to: HexBytes,
                            value: float = None, wait_until_complete: bool = True) -> Tuple[int, HexBytes]:
        if value is None:
            value = self.address_balance(address_from)
        nonce = self.address_nonce(address_from)
        tx = dict(
            nonce=nonce,
            to=address_to,
            value=value - self.total_commission,
            gas=self.gas,
            gasPrice=self.gas_price
        )
        signed_tx = self.client.eth.account.sign_transaction(tx, private_key)
        tx_hash = self.client.eth.send_raw_transaction(signed_tx.rawTransaction)
        if wait_until_complete:
            self.client.eth.wait_for_transaction_receipt(tx_hash)
        return self.address_nonce(address_from), tx_hash

    def address_balance(self, address: HexBytes) -> int:
        return self.client.eth.get_balance(address)

    def address_nonce(self, address: HexBytes) -> int:
        return self.client.eth.get_transaction_count(address)

    def create_private_key(self) -> HexBytes:
        return '0x' + secrets.token_hex(32)

    def check_address(self, address: HexBytes) -> bool:
        return self.client.isAddress(address)


# may be for future currencies, some flexibility for serializer, view...
nodes = dict.fromkeys(CURRENCIES.KEYS)
nodes[CURRENCIES.ETH] = EthereumNode()
