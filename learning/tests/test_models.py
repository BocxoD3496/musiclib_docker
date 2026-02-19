import time
from django.test import TestCase
from django.db import IntegrityError
from django.utils import timezone

from learning.models import (
    Language, Lesson, Card, UserLessonProgress, CardReview,
    QuizQuestion, QuizChoice, UserQuizAttempt
)
from .utils import create_user, seed_language_lesson_cards


class ModelCreateTests(TestCase):
    def test_create_language(self):
        lang = Language.objects.create(name="English", code="en")
        self.assertIsNotNone(lang.id)

    def test_lesson_fk_language(self):
        lang = Language.objects.create(name="English", code="en")
        lesson = Lesson.objects.create(language=lang, title="L1", description="d", order=1)
        self.assertEqual(lesson.language_id, lang.id)

    def test_card_fk_lesson(self):
        _, lesson, cards = seed_language_lesson_cards(cards=1)
        self.assertEqual(cards[0].lesson_id, lesson.id)

    def test_user_progress_unique(self):
        user = create_user()
        _, lesson, _ = seed_language_lesson_cards(cards=1)
        UserLessonProgress.objects.create(user=user, lesson=lesson, current_index=0)
        with self.assertRaises(IntegrityError):
            UserLessonProgress.objects.create(user=user, lesson=lesson, current_index=0)

    def test_card_review_unique(self):
        user = create_user()
        _, lesson, cards = seed_language_lesson_cards(cards=1)
        CardReview.objects.create(user=user, card=cards[0], status="new")
        with self.assertRaises(IntegrityError):
            CardReview.objects.create(user=user, card=cards[0], status="new")

    def test_created_updated_autofill(self):
        lang = Language.objects.create(name="English", code="en")
        self.assertIsNotNone(lang.created_at)
        self.assertIsNotNone(lang.updated_at)

    def test_updated_at_changes_on_save(self):
        lang = Language.objects.create(name="English", code="en")
        old_updated = lang.updated_at
        time.sleep(0.01)  # чтобы timestamp точно изменился
        lang.name = "English Updated"
        lang.save()
        lang.refresh_from_db()
        self.assertGreater(lang.updated_at, old_updated)


class QuizModelsSmokeTests(TestCase):
    def test_quiz_models_create(self):
        """
        Если есть миграции под Quiz-модели — этот тест пройдёт.
        Если миграций нет, будет ошибка таблицы (и это полезный сигнал).
        """
        user = create_user()
        _, lesson, _ = seed_language_lesson_cards(cards=1)

        q = QuizQuestion.objects.create(lesson=lesson, order=1, text="Q1?", is_published=True)
        c1 = QuizChoice.objects.create(question=q, text="A", is_correct=True)
        attempt = UserQuizAttempt.objects.create(user=user, question=q, choice=c1, is_correct=True)

        self.assertIsNotNone(q.id)
        self.assertIsNotNone(c1.id)
        self.assertIsNotNone(attempt.id)
