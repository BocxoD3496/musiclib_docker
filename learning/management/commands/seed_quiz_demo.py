from django.core.management.base import BaseCommand
from django.db import transaction

from learning.models import Language, Lesson, QuizQuestion, QuizChoice, Card


class Command(BaseCommand):
    help = "Seed demo lessons + published quiz questions (simple, visible functionality)."

    @transaction.atomic
    def handle(self, *args, **options):
        # Languages
        en, _ = Language.objects.get_or_create(code="en", defaults={"name": "Английский"})
        ru, _ = Language.objects.get_or_create(code="ru", defaults={"name": "Русский (тестовый)"})

        # Lessons (fictional)
        lesson_en_1, _ = Lesson.objects.get_or_create(
            language=en, order=1,
            defaults={"title": "EN • Super Easy 1", "description": "Очень простые вопросы для демонстрации."}
        )
        lesson_en_2, _ = Lesson.objects.get_or_create(
            language=en, order=2,
            defaults={"title": "EN • Super Easy 2", "description": "Ещё проще — чтобы было видно правильно/неправильно."}
        )
        lesson_ru_1, _ = Lesson.objects.get_or_create(
            language=ru, order=1,
            defaults={"title": "RU • Логика 1", "description": "Простейшие вопросы на внимательность."}
        )

        # Quiz dataset: (lesson, order, question_text, [(choice_text, is_correct), ...])
        quiz_data = [
            (lesson_en_1, 1, "Перевод слова 'Hello'?", [("Пока", False), ("Привет", True), ("Спасибо", False), ("Пожалуйста", False)]),
            (lesson_en_1, 2, "Перевод слова 'Cat'?", [("Кот", True), ("Собака", False), ("Птица", False), ("Рыба", False)]),
            (lesson_en_1, 3, "Сколько будет 2 + 2?", [("3", False), ("4", True), ("5", False), ("22", False)]),
            (lesson_en_1, 4, "Выбери правильную форму: I ___ a student.", [("is", False), ("am", True), ("are", False), ("be", False)]),
            (lesson_en_1, 5, "Перевод 'Thank you'?", [("Спасибо", True), ("Извини", False), ("Привет", False), ("Пока", False)]),

            (lesson_en_2, 1, "Перевод 'Apple'?", [("Яблоко", True), ("Аптека", False), ("Молоко", False), ("Книга", False)]),
            (lesson_en_2, 2, "Перевод 'Book'?", [("Бук", False), ("Книга", True), ("Кот", False), ("Стол", False)]),
            (lesson_en_2, 3, "Сколько будет 10 / 2?", [("2", False), ("4", False), ("5", True), ("10", False)]),
            (lesson_en_2, 4, "Выбери правильное: He ___ my friend.", [("are", False), ("am", False), ("is", True), ("be", False)]),
            (lesson_en_2, 5, "Перевод 'Goodbye'?", [("Добрый", False), ("До свидания", True), ("Пожалуйста", False), ("Спасибо", False)]),

            (lesson_ru_1, 1, "Столица России?", [("Москва", True), ("Санкт-Петербург", False), ("Казань", False), ("Сочи", False)]),
            (lesson_ru_1, 2, "Сколько букв в слове «кот»?", [("2", False), ("3", True), ("4", False), ("5", False)]),
            (lesson_ru_1, 3, "Выбери четное число:", [("7", False), ("9", False), ("10", True), ("11", False)]),
            (lesson_ru_1, 4, "Продолжи последовательность: 1, 2, 3, ___", [("4", True), ("5", False), ("6", False), ("0", False)]),
            (lesson_ru_1, 5, "Лишнее слово:", [("яблоко", False), ("груша", False), ("банан", False), ("стол", True)]),
        ]


        created_q = 0
        created_c = 0

        for lesson, order, q_text, choices in quiz_data:
            q, was_created = QuizQuestion.objects.get_or_create(
                lesson=lesson,
                order=order,
                defaults={"text": q_text, "is_published": True},
            )
            if not was_created:
                # Ensure it is published and text is up-to-date (optional)
                if (not q.is_published) or (q.text != q_text):
                    q.text = q_text
                    q.is_published = True
                    q.save(update_fields=["text", "is_published", "updated_at"])
            else:
                created_q += 1

            # Create/refresh choices
            # If choices already exist, do not duplicate; keep it simple:
            for text, is_correct in choices:
                c, c_created = QuizChoice.objects.get_or_create(
                    question=q,
                    text=text,
                    defaults={"is_correct": is_correct},
                )
                if not c_created and c.is_correct != is_correct:
                    c.is_correct = is_correct
                    c.save(update_fields=["is_correct", "updated_at"])
                if c_created:
                    created_c += 1

        cards_data = [
            # lesson, front, back, example
            (lesson_en_1, "Hello", "Привет", "Hello!"),
            (lesson_en_1, "Cat", "Кот", "A cat."),
            (lesson_en_1, "Thank you", "Спасибо", "Thank you!"),

            (lesson_en_2, "Apple", "Яблоко", "An apple."),
            (lesson_en_2, "Book", "Книга", "A book."),
            (lesson_en_2, "Goodbye", "До свидания", "Goodbye!"),

            (lesson_ru_1, "Столица России", "Москва", "Вопрос-ответ."),
            (lesson_ru_1, "Чётное число", "10", "10 — чётное."),
        ]
        created_cards = 0
        for lesson, front, back, ex in cards_data:
            obj, was_created = Card.objects.get_or_create(
                lesson=lesson,
                front_text=front,
                defaults={"back_text": back, "example": ex},
            )
            if was_created:
                created_cards += 1


        self.stdout.write(self.style.SUCCESS(
            f"Seed OK ✅ Questions created: {created_q}, choices created: {created_c}. "
            f"All questions are published."
        ))
