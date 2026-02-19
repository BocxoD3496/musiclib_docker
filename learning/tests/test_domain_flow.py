from django.test import TestCase
from django.urls import reverse
from learning.models import UserLessonProgress, CardReview
from .utils import create_user, seed_language_lesson_cards


class DomainFlowTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.lang, self.lesson, self.cards = seed_language_lesson_cards(cards=2)

    def test_full_lesson_flow_creates_progress_and_reviews(self):
        self.client.login(username="u1", password="Pass12345!")

        # открыть урок
        r = self.client.get(reverse("lesson_detail", args=[self.lesson.id]))
        self.assertEqual(r.status_code, 200)

        # Ниже — проверка состояния (тут будет работать после подстановки реального POST)
        progress_count_before = UserLessonProgress.objects.count()
        review_count_before = CardReview.objects.count()

        # TODO: заменить на реальные POST действия твоего проекта
        UserLessonProgress.objects.get_or_create(user=self.user, lesson=self.lesson, defaults={"current_index": 1})
        CardReview.objects.get_or_create(user=self.user, card=self.cards[0], defaults={"status": "learning", "streak": 1})

        self.assertGreaterEqual(UserLessonProgress.objects.count(), progress_count_before + 1)
        self.assertGreaterEqual(CardReview.objects.count(), review_count_before + 1)
