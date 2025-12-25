import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_create_user():
    user = User.objects.create_user(
        username='test', email='test@admin.com', password='1234'
    )
    assert user.username == 'test'
    assert user.email == 'test@admin.com'
