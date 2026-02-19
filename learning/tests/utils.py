from django.contrib.auth import get_user_model
from learning.models import Language, Lesson, Card

User = get_user_model()

def create_user(username="u1", email="u1@example.com", password="Pass12345!"):
    return User.objects.create_user(username=username, email=email, password=password)

def create_superuser(username="admin", email="admin@example.com", password="Pass12345!"):
    return User.objects.create_superuser(username=username, email=email, password=password)

def seed_language_lesson_cards(lang_code="en", cards=3):
    lang = Language.objects.create(name="English", code=lang_code)
    lesson = Lesson.objects.create(language=lang, title="Lesson 1", description="desc", order=1)
    card_objs = []
    for i in range(cards):
        card_objs.append(Card.objects.create(
            lesson=lesson,
            front_text=f"front {i}",
            back_text=f"back {i}",
            example=f"ex {i}",
        ))
    return lang, lesson, card_objs
