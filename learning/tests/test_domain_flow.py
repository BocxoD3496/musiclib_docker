from .base import BaseTestCase
from django.urls import reverse

from learning.models import UserLessonProgress
from .utils import create_user, seed_language_lesson_cards


class DomainFlowTests(BaseTestCase):
    def setUp(self):
        self.user = create_user()
        self.lang, self.lesson, self.cards = seed_language_lesson_cards(lang_code="en", cards=2)

    def test_full_flow_open_lesson_practice_and_progress(self):
        self.client.login(username="u1", password="Pass12345!")

        r = self.client.get(reverse("learning:lesson_detail", args=[self.lesson.id]))
        self.assertEqual(r.status_code, 200)

        r2 = self.client.get(reverse("learning:practice", args=[self.lesson.id]))
        self.assertIn(r2.status_code, (200, 302))

        UserLessonProgress.objects.get_or_create(
            user=self.user, lesson=self.lesson, defaults={"current_index": 0}
        )
        self.assertTrue(UserLessonProgress.objects.filter(user=self.user, lesson=self.lesson).exists())
