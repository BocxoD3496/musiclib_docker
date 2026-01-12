from django.core.management.base import BaseCommand
from learning.models import Language, Lesson, Card

class Command(BaseCommand):
    help = "Create demo languages/lessons/cards for quick testing."

    def handle(self, *args, **options):
        en, _ = Language.objects.get_or_create(code="en", defaults={"name": "Английский"})
        de, _ = Language.objects.get_or_create(code="de", defaults={"name": "Немецкий"})

        lesson1, _ = Lesson.objects.get_or_create(language=en, order=1, defaults={
            "title": "Базовые приветствия",
            "description": "Небольшой урок: приветствия и простые фразы."
        })
        lesson2, _ = Lesson.objects.get_or_create(language=en, order=2, defaults={
            "title": "Еда и напитки",
            "description": "Слова и выражения про еду."
        })
        lesson3, _ = Lesson.objects.get_or_create(language=de, order=1, defaults={
            "title": "Hallo & Tschüss",
            "description": "Приветствия по-немецки."
        })

        cards = [
            (lesson1, "Hello", "Привет", "Hello! How are you?"),
            (lesson1, "Good morning", "Доброе утро", "Good morning, everyone!"),
            (lesson1, "Thank you", "Спасибо", "Thank you for your help."),
            (lesson2, "Water", "Вода", "A glass of water, please."),
            (lesson2, "Coffee", "Кофе", "I like coffee."),
            (lesson3, "Hallo", "Привет", "Hallo! Wie geht's?"),
            (lesson3, "Tschüss", "Пока", "Tschüss! Bis bald!"),
        ]

        created = 0
        for lesson, front, back, ex in cards:
            obj, was_created = Card.objects.get_or_create(
                lesson=lesson,
                front_text=front,
                defaults={"back_text": back, "example": ex},
            )
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Seed complete. New cards created: {created}"))
