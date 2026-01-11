import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from tests.factories import UserFactory


User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def admin_user():
    return UserFactory(is_staff=True, is_superuser=True)


@pytest.fixture
def auth_client(api_client, user):
    from rest_framework.authtoken.models import Token

    token, _ = Token.objects.get_or_create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return api_client
