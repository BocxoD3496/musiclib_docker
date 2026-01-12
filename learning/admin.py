from django.contrib import admin
from .admin_site import admin_site
from .models import Language, Lesson, Card, UserLessonProgress, CardReview
from .models import QuizQuestion, QuizChoice, UserQuizAttempt

@admin.register(Language, site=admin_site)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "updated_at")
    search_fields = ("name", "code")

@admin.register(Lesson, site=admin_site)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "language", "order", "updated_at")
    list_filter = ("language",)
    search_fields = ("title", "description")

@admin.register(Card, site=admin_site)
class CardAdmin(admin.ModelAdmin):
    list_display = ("front_text", "lesson", "updated_at")
    list_filter = ("lesson__language", "lesson")
    search_fields = ("front_text", "back_text", "example")

@admin.register(UserLessonProgress, site=admin_site)
class UserLessonProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "lesson", "current_index", "correct", "wrong", "completed", "updated_at")
    list_filter = ("completed", "lesson__language")
    search_fields = ("user__username", "lesson__title")

@admin.register(CardReview, site=admin_site)
class CardReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "card", "status", "streak", "next_due_at", "updated_at")
    list_filter = ("status",)
    search_fields = ("user__username", "card__front_text")

class QuizChoiceInline(admin.TabularInline):
    model = QuizChoice
    extra = 3

@admin.register(QuizQuestion, site=admin_site)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ("lesson", "order", "text", "is_published", "updated_at")
    list_filter = ("is_published", "lesson__language")
    search_fields = ("text",)
    ordering = ("lesson", "order")
    inlines = [QuizChoiceInline]

@admin.register(UserQuizAttempt, site=admin_site)
class UserQuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "question", "choice", "is_correct", "updated_at")
    list_filter = ("is_correct", "question__lesson__language")
    search_fields = ("user__username", "question__text", "choice__text")
