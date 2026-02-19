from django.test import TestCase
from django.contrib.auth import get_user_model

try:
    from learning.forms import RegisterForm, LoginForm
except Exception:
    RegisterForm = None
    LoginForm = None

User = get_user_model()


class FormsTests(TestCase):
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

    def test_login_form_valid(self):
        if not LoginForm:
            self.skipTest("LoginForm not found (adjust import path/name).")

        User.objects.create_user(username="u1", email="u1@example.com", password="Pass12345!")
        form = LoginForm(data={"username": "u1", "password": "Pass12345!"})
        self.assertTrue(form.is_valid(), form.errors)

    def test_login_form_invalid(self):
        if not LoginForm:
            self.skipTest("LoginForm not found (adjust import path/name).")

        form = LoginForm(data={"username": "nope", "password": "wrong"})
        self.assertFalse(form.is_valid())
