from rest_framework import serializers
from .models import Language, Lesson, Card, UserLessonProgress

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ["id", "name", "code", "created_at", "updated_at"]

class LessonSerializer(serializers.ModelSerializer):
    language = LanguageSerializer(read_only=True)
    language_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Lesson
        fields = ["id", "language", "language_id", "title", "description", "order", "created_at", "updated_at"]

class CardSerializer(serializers.ModelSerializer):
    lesson_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Card
        fields = ["id", "lesson", "lesson_id", "front_text", "back_text", "example", "image", "created_at", "updated_at"]
        read_only_fields = ["lesson"]

class UserLessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLessonProgress
        fields = ["id", "lesson", "current_index", "correct", "wrong", "completed", "created_at", "updated_at"]
