from django.test import TestCase
from django.urls import reverse

from .utils import create_user, create_superuser


class AuthzTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.admin = create_superuser()

    def test_guest_cannot_access_dashboard(self):
        url = reverse("dashboard")
        r = self.client.get(url)
        self.assertIn(r.status_code, (301, 302, 403))

    def test_user_can_access_dashboard(self):
        self.client.login(username="u1", password="Pass12345!")
        url = reverse("dashboard")
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

    def test_user_cannot_access_admin(self):
        self.client.login(username="u1", password="Pass12345!")
        r = self.client.get("/admin/")
        self.assertIn(r.status_code, (302, 403))

    def test_admin_can_access_admin(self):
        self.client.login(username="admin", password="Pass12345!")
        r = self.client.get("/admin/")
        self.assertIn(r.status_code, (200, 302))
