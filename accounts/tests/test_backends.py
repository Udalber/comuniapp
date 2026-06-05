from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.backends import EmailBackend

User = get_user_model()


class EmailBackendTests(TestCase):
    def setUp(self):
        self.backend = EmailBackend()
        self.user = User.objects.create_user(
            username="maria@example.com",
            email="maria@example.com",
            password="SecurePass123!",
            first_name="María",
        )

    def test_authenticates_with_email(self):
        user = self.backend.authenticate(
            request=None,
            email="maria@example.com",
            password="SecurePass123!",
        )
        self.assertEqual(user, self.user)

    def test_authenticates_with_username_kwarg(self):
        user = self.backend.authenticate(
            request=None,
            username="maria@example.com",
            password="SecurePass123!",
        )
        self.assertEqual(user, self.user)

    def test_email_is_case_insensitive(self):
        user = self.backend.authenticate(
            request=None,
            email="MARIA@EXAMPLE.COM",
            password="SecurePass123!",
        )
        self.assertEqual(user, self.user)

    def test_wrong_password_returns_none(self):
        user = self.backend.authenticate(
            request=None,
            email="maria@example.com",
            password="wrong-password",
        )
        self.assertIsNone(user)

    def test_unknown_email_returns_none(self):
        user = self.backend.authenticate(
            request=None,
            email="otro@example.com",
            password="SecurePass123!",
        )
        self.assertIsNone(user)
