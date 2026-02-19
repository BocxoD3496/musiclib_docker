import io
from django.test import TestCase
from django.urls import reverse
from openpyxl import load_workbook

from .utils import create_superuser, seed_language_lesson_cards


class AdminExportTests(TestCase):
    def setUp(self):
        self.admin = create_superuser()
        seed_language_lesson_cards(lang_code="en", cards=1)

    def test_export_requires_admin(self):
        url = reverse("admin_report_export")
        r = self.client.get(url)
        self.assertIn(r.status_code, (302, 403))

    def test_export_returns_valid_xlsx(self):
        self.client.login(username="admin", password="Pass12345!")
        url = reverse("admin_report_export")
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

        # xlsx — это zip, начинается с PK
        self.assertTrue(r.content.startswith(b"PK\x03\x04"))

        wb = load_workbook(filename=io.BytesIO(r.content))
        self.assertGreaterEqual(len(wb.sheetnames), 1)
