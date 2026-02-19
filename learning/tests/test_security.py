from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import identify_hasher
from .utils import create_user
from django.urls import reverse
from .utils import seed_language_lesson_cards
from .utils import create_user, seed_language_lesson_cards
from learning.models import Card

User = get_user_model()

class PasswordHashTests(TestCase):
    def test_password_is_hashed(self):
        u = create_user(username="u2", email="u2@example.com", password="Pass12345!")
        u.refresh_from_db()
        self.assertNotEqual(u.password, "Pass12345!")
        # строка имеет формат "algo$..."
        self.assertIn("$", u.password)
        identify_hasher(u.password)  # не должно упасть

class SqlInjectionTests(TestCase):
    def setUp(self):
        seed_language_lesson_cards(cards=1)

    def test_search_sqli_payload_does_not_crash(self):
        payload = "' OR 1=1 --"
        url = reverse("lessons_list") + f"?q={payload}"
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

class XssTests(TestCase):
    def setUp(self):
        self.user = create_user()
        _, self.lesson, _ = seed_language_lesson_cards(cards=0)
        self.client.login(username="u1", password="Pass12345!")

    def test_xss_payload_is_escaped(self):
        xss = '<script>alert("x")</script>'
        Card.objects.create(lesson=self.lesson, front_text=xss, back_text="b", example="e")

        r = self.client.get(reverse("lesson_detail", args=[self.lesson.id]))
        self.assertEqual(r.status_code, 200)

        self.assertNotContains(r, xss, html=False)
        self.assertContains(r, "&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;", html=False)
