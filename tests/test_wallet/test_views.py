import json
import pytest
from model_bakery import baker
from rest_framework.reverse import reverse
from crypto_wallet.wallet.models import Wallet


class TestWalletEndpoints:
    pytestmark = pytest.mark.django_db
    endpoint = reverse('wallet-list')

    def test_list(self, api_client) -> None:
        baker.make(Wallet, _quantity=10)
        response = api_client().get(
            self.endpoint
        )
        assert response.status_code == 200
        assert len(json.loads(response.content)) == 10

    def test_create(self, api_client, eth_node) -> None:
        data = {
            'currency': eth_node.currency,
        }
        response = api_client().post(
            self.endpoint,
            data=data,
            format='json'
        )
        response_fields = json.loads(response.content).keys()
        expected_fields = {'currency', 'address'}
        assert response.status_code == 201, response.content
        assert expected_fields == set(response_fields)
        invalid_data = {
            'currency': 'BCH'
        }
        response = api_client().post(
            self.endpoint,
            data=invalid_data,
            format='json'
        )
        assert response.status_code == 400

    def test_transfer(self, api_client, eth_node, eth_accounts_with_balance, eth_internal_wallet) -> None:
        # transfer money to internal wallet first
        address1, addr1_private_key = eth_accounts_with_balance[0]
        address2 = eth_internal_wallet.address
        balance_from = eth_node.address_balance(address1)
        balance_to = eth_node.address_balance(address2)
        eth_node.transfer_to_address(
            private_key=addr1_private_key,
            address_from=address1,
            address_to=address2
        )
        assert eth_node.address_balance(address2) == balance_from + balance_to - eth_node.total_commission

        # send money back
        url = reverse('wallet-transfer')
        balance_from = eth_node.address_balance(address2)
        balance_to = eth_node.address_balance(address1)
        data = {
            "_from": address2,
            '_to': address1,
            'currency': eth_node.currency,
        }
        response = api_client().post(
            url,
            data=data,
            format='json'
        )
        assert response.status_code == 201, response.content
        assert eth_node.address_balance(address1) == balance_to + balance_from - eth_node.total_commission
        assert eth_node.address_balance(address2) == 0
        response_json = json.loads(response.content)
        expected_fields = {'hash', 'nonce'}
        assert expected_fields == set(response_json)
        assert eth_node.address_nonce(address2) == response_json['nonce']

        # try to send from wallet with zero balance
        response = api_client().post(
            url,
            data=data,
            format='json'
        )
        assert response.status_code == 400
