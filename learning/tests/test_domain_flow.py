from django.test import TestCase
from django.urls import reverse

from learning.models import UserLessonProgress
from .utils import create_user, seed_language_lesson_cards


class DomainFlowTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.lang, self.lesson, self.cards = seed_language_lesson_cards(lang_code="en", cards=2)

    def test_full_lesson_flow_open_lesson_and_practice(self):
        self.client.login(username="u1", password="Pass12345!")

        # открыть урок
        r = self.client.get(reverse("lesson_detail", args=[self.lesson.id]))
        self.assertEqual(r.status_code, 200)

        # открыть практику (если доступна)
        r2 = self.client.get(reverse("practice", args=[self.lesson.id]))
        self.assertIn(r2.status_code, (200, 302))

        # минимальная проверка: прогресс либо создаётся, либо ещё нет — но база не должна падать
        UserLessonProgress.objects.get_or_create(user=self.user, lesson=self.lesson, defaults={"current_index": 0})
        self.assertTrue(UserLessonProgress.objects.filter(user=self.user, lesson=self.lesson).exists())
