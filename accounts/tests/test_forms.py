from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.forms import ProfileForm, RegisterForm

User = get_user_model()


class RegisterFormTests(TestCase):
    def test_creates_user_with_username_equal_to_email(self):
        form = RegisterForm(
            data={
                "full_name": "Ana López",
                "email": "ana.lopez@example.com",
                "password": "SecurePass123!",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.username, "ana.lopez@example.com")
        self.assertEqual(user.email, "ana.lopez@example.com")
        self.assertEqual(user.first_name, "Ana")
        self.assertEqual(user.last_name, "López")

    def test_rejects_duplicate_email(self):
        User.objects.create_user(
            username="existente@example.com",
            email="existente@example.com",
            password="SecurePass123!",
        )
        form = RegisterForm(
            data={
                "full_name": "Otro Usuario",
                "email": "existente@example.com",
                "password": "SecurePass123!",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class ProfileFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="perfil@example.com",
            email="perfil@example.com",
            password="SecurePass123!",
            first_name="Perfil",
            last_name="Uno",
        )
        User.objects.create_user(
            username="otro@example.com",
            email="otro@example.com",
            password="SecurePass123!",
        )

    def test_allows_own_email(self):
        form = ProfileForm(
            self.user,
            data={
                "first_name": "Perfil",
                "last_name": "Uno",
                "email": "perfil@example.com",
            },
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_rejects_duplicate_email_excluding_self(self):
        form = ProfileForm(
            self.user,
            data={
                "first_name": "Perfil",
                "last_name": "Uno",
                "email": "otro@example.com",
            },
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
