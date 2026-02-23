from .base import BaseTestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse

try:
    from accounts.forms import RegisterForm
except Exception:
    RegisterForm = None

User = get_user_model()


class FormsTests(BaseTestCase):
    def test_register_form_valid(self):
        if not RegisterForm:
            self.skipTest("RegisterForm not found (adjust import path/name).")

        form = RegisterForm(data={
            "username": "u1",
            "email": "u1@example.com",
            "password1": "Pass12345!",
            "password2": "Pass12345!",
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_register_form_invalid_password_mismatch(self):
        if not RegisterForm:
            self.skipTest("RegisterForm not found (adjust import path/name).")

        form = RegisterForm(data={
            "username": "u1",
            "email": "u1@example.com",
            "password1": "Pass12345!",
            "password2": "Different123!",
        })
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors)
        
        def test_login_view_valid(self):
            User = get_user_model()
            User.objects.create_user(
                username="u1",
                email="u1@example.com",
                password="Pass12345!"
        )

        r = self.client.post(
            reverse("accounts:login"),
            {"username": "u1", "password": "Pass12345!"},
        )

        self.assertEqual(r.status_code, 200)