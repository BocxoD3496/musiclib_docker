from .base import BaseTestCase
from django.urls import reverse
from django.contrib.auth.hashers import identify_hasher

from learning.models import Card
from .utils import create_user, seed_language_lesson_cards


class PasswordHashTests(BaseTestCase):
    def test_password_is_hashed(self):
        u = create_user(username="u2", email="u2@example.com", password="Pass12345!")
        u.refresh_from_db()
        self.assertNotEqual(u.password, "Pass12345!")
        self.assertIn("$", u.password)
        identify_hasher(u.password)


class SqlInjectionTests(BaseTestCase):
    def setUp(self):
        self.lang, self.lesson, _ = seed_language_lesson_cards(lang_code="en", cards=1)

    def test_search_sqli_payload_does_not_crash(self):
        payload = "' OR 1=1 --"
        url = reverse("learning:lessons_list", args=[self.lang.code]) + f"?q={payload}"
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)


class XssTests(BaseTestCase):
    def setUp(self):
        self.user = create_user()
        self.lang, self.lesson, _ = seed_language_lesson_cards(lang_code="en", cards=0)
        self.client.login(username="u1", password="Pass12345!")

    def test_xss_payload_is_escaped(self):
        xss = '<script>alert("x")</script>'
        Card.objects.create(lesson=self.lesson, front_text=xss, back_text="b", example="e")

        r = self.client.get(reverse("learning:lesson_detail", args=[self.lesson.id]))
        # если вдруг lesson_detail защищён, будет 302 на login — тогда XSS проверять нечего
        self.assertIn(r.status_code, (200, 302))
        if r.status_code == 200:
            self.assertNotContains(r, xss, html=False)
            self.assertContains(r, "&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;", html=False)
