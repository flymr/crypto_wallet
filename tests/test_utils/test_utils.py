import pytest
from django.contrib.auth.models import User
from crypto_wallet.utils import get_or_none


@pytest.mark.django_db
def test_get_or_none():
    User.objects.create(username='test_user', first_name='bob')
    User.objects.create(username='test_user2', first_name='bob')
    assert get_or_none(User, username='test_user')
    assert get_or_none(User, username='test_user2', first_name='bob')
    assert not get_or_none(User, username='invalid_user')
    assert not get_or_none(User, first_name='bob')
