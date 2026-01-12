from django.conf import settings
from django.db import models

class TimeStampedModel(models.Model):
    """Abstract base model with common timestamps."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Language(TimeStampedModel):
    name = models.CharField(max_length=64, unique=True)
    code = models.CharField(max_length=16, unique=True, help_text="ISO code, e.g. en, de, fr")

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"

class Lesson(TimeStampedModel):
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("language", "order")
        ordering = ("language__name", "order")

    def __str__(self) -> str:
        return f"{self.language.code}: {self.title}"

class Card(TimeStampedModel):
    """Flashcard for a lesson."""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="cards")
    front_text = models.CharField(max_length=200, help_text="Question / prompt")
    back_text = models.CharField(max_length=200, help_text="Answer / translation")
    example = models.TextField(blank=True)
    image = models.ImageField(upload_to="cards/", blank=True, null=True)

    class Meta:
        ordering = ("id",)

    def __str__(self) -> str:
        return f"Card #{self.pk} ({self.lesson.title})"

class UserLessonProgress(TimeStampedModel):
    """Progress by user on a lesson (saved only for authenticated users)."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lesson_progress")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="user_progress")
    current_index = models.PositiveIntegerField(default=0)
    correct = models.PositiveIntegerField(default=0)
    wrong = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "lesson")

    def __str__(self) -> str:
        return f"{self.user} - {self.lesson} ({'done' if self.completed else 'in progress'})"

class CardReview(TimeStampedModel):
    """Very simple spaced-repetition-like review tracking per card."""
    STATUS_CHOICES = [
        ("new", "New"),
        ("learning", "Learning"),
        ("known", "Known"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="card_reviews")
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="reviews")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="new")
    last_reviewed_at = models.DateTimeField(blank=True, null=True)
    next_due_at = models.DateTimeField(blank=True, null=True)
    streak = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("user", "card")

    def __str__(self) -> str:
        return f"{self.user} - {self.card_id} ({self.status})"

class QuizQuestion(TimeStampedModel):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="quiz_questions")
    text = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=1)
    is_published = models.BooleanField(default=False)  # модерация

    class Meta:
        unique_together = ("lesson", "order")
        ordering = ("lesson_id", "order")

    def __str__(self):
        return f"Q{self.order}: {self.text[:40]}"


class QuizChoice(TimeStampedModel):
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{'✅' if self.is_correct else '❌'} {self.text[:40]}"


class UserQuizAttempt(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quiz_attempts")
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name="attempts")
    choice = models.ForeignKey(QuizChoice, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "question")  # 1 актуальная попытка на вопрос

    def __str__(self):
        return f"{self.user} -> {self.question_id} ({'OK' if self.is_correct else 'NO'})"
