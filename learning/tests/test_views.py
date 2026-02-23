from .base import BaseTestCase
from django.urls import reverse

from .utils import create_user, seed_language_lesson_cards


class ViewsStatusTests(BaseTestCase):
    def setUp(self):
        self.user = create_user()
        self.lang, self.lesson, self.cards = seed_language_lesson_cards(lang_code="en", cards=3)

    def test_home_200(self):
        # reverse("home") у тебя не резолвится в shell, поэтому тестируем по фактическому пути
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)

    def test_lessons_list_200_anonymous(self):
        url = reverse("learning:lessons_list", args=[self.lang.code])
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

    def test_lesson_detail_requires_login_or_open(self):
        url = reverse("learning:lesson_detail", args=[self.lesson.id])
        r = self.client.get(url)
        self.assertIn(r.status_code, (200, 302))

    def test_lesson_detail_200_logged_in(self):
        self.client.login(username="u1", password="Pass12345!")
        url = reverse("learning:lesson_detail", args=[self.lesson.id])
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

    def test_search_returns_expected(self):
        url = reverse("learning:lessons_list", args=[self.lang.code]) + "?q=Lesson"
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Lesson 1")
