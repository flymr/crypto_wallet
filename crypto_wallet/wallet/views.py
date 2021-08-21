from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from crypto_wallet.nodes import nodes
from crypto_wallet.wallet.models import Wallet
from crypto_wallet.wallet.serializers import WalletSerializer, TransferWalletSerializer, TransferResponseSerializer


class WalletViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    serializer_class = WalletSerializer
    queryset = Wallet.objects.all()

    def get_serializer_class(self):
        if self.action == 'transfer':
            return TransferWalletSerializer
        else:
            return self.serializer_class

    @swagger_auto_schema(responses={201: TransferResponseSerializer})
    @action(methods=['POST'], detail=False, url_path='transfer')
    def transfer(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, *args, **kwargs)
        if serializer.is_valid():
            validated_data = serializer.data
            wallet = validated_data['wallet']
            try:
                nonce, tx_hash = nodes[wallet.currency].transfer_to_address(
                    private_key=wallet.private_key,
                    address_from=wallet.address,
                    address_to=validated_data['_to'],
                    value=validated_data['balance'],
                )
                data = TransferResponseSerializer(dict(nonce=nonce, hash=tx_hash)).data
                return Response(data=data, status=status.HTTP_201_CREATED)
            except ValueError as e:
                return Response(data=e.args, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
