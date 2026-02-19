from django.test import TestCase
from django.urls import reverse
from .utils import create_user, seed_language_lesson_cards


class ViewsStatusTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.lang, self.lesson, self.cards = seed_language_lesson_cards(cards=3)

    def test_home_200(self):
        url = reverse("home")
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

    def test_lessons_list_200_anonymous(self):
        url = reverse("lessons_list")
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

    def test_lesson_detail_requires_login(self):
        url = reverse("lesson_detail", args=[self.lesson.id])
        r = self.client.get(url)
        # обычно 302 на login
        self.assertIn(r.status_code, (302, 301))

    def test_lesson_detail_200_logged_in(self):
        self.client.login(username="u1", password="Pass12345!")
        url = reverse("lesson_detail", args=[self.lesson.id])
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

    def test_search_returns_expected(self):
        url = reverse("lessons_list") + "?q=Lesson"
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Lesson 1")
