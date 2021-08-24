from rest_framework import serializers
from crypto_wallet.constants import CURRENCIES
from crypto_wallet.nodes import nodes
from crypto_wallet.utils import get_or_none
from crypto_wallet.wallet.models import Wallet


class WalletSerializer(serializers.ModelSerializer):

    class Meta:
        model = Wallet
        fields = (
            'currency',
            'address',
        )
        read_only_fields = (
            'address',
        )

    def create(self, validated_data):
        address, private_key = nodes[validated_data['currency']].create_address()
        validated_data.update(address=address, private_key=private_key)
        wallet = super(WalletSerializer, self).create(validated_data)
        return wallet


class TransferWalletSerializer(serializers.Serializer):
    _from = serializers.CharField()
    _to = serializers.CharField()
    currency = serializers.ChoiceField(choices=CURRENCIES.CHOICES)

    def validate(self, attrs):
        wallet = get_or_none(Wallet, address=attrs.get('_from'))
        balance = nodes[wallet.currency].address_balance(wallet.address) if wallet else None
        attrs.update(
            balance=balance,
            wallet=wallet
        )
        wallet = attrs['wallet']
        if not attrs['wallet']:
            raise serializers.ValidationError('Wallet is invalid')
        if not nodes[wallet.currency].check_address(attrs.get('_to')):
            raise serializers.ValidationError('Target wallet is invalid')
        if attrs['balance'] < nodes[wallet.currency].total_commission:
            raise serializers.ValidationError('Is not enough money for commission')
        return attrs

    def to_representation(self, data):
        # need because without overriding we will lose all values not included in serializer fields
        return data


class TransferResponseSerializer(serializers.Serializer):
    nonce = serializers.IntegerField()
    hash = serializers.CharField()
