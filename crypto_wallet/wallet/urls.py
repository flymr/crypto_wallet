from rest_framework import routers

from crypto_wallet.wallet.views import WalletViewSet

router = routers.DefaultRouter()
router.register(r'wallet', WalletViewSet)

urlpatterns = router.urls
