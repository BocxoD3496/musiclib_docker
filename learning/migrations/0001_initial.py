# Generated manually for the assignment (initial schema).
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Language",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=64, unique=True)),
                ("code", models.CharField(help_text="ISO code, e.g. en, de, fr", max_length=16, unique=True)),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="Lesson",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=120)),
                ("description", models.TextField(blank=True)),
                ("order", models.PositiveIntegerField(default=1)),
                ("language", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="lessons", to="learning.language")),
            ],
            options={
                "ordering": ("language__name", "order"),
                "unique_together": {("language", "order")},
            },
        ),
        migrations.CreateModel(
            name="Card",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("front_text", models.CharField(help_text="Question / prompt", max_length=200)),
                ("back_text", models.CharField(help_text="Answer / translation", max_length=200)),
                ("example", models.TextField(blank=True)),
                ("image", models.ImageField(blank=True, null=True, upload_to="cards/")),
                ("lesson", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="cards", to="learning.lesson")),
            ],
            options={"ordering": ("id",)},
        ),
        migrations.CreateModel(
            name="UserLessonProgress",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("current_index", models.PositiveIntegerField(default=0)),
                ("correct", models.PositiveIntegerField(default=0)),
                ("wrong", models.PositiveIntegerField(default=0)),
                ("completed", models.BooleanField(default=False)),
                ("lesson", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="user_progress", to="learning.lesson")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="lesson_progress", to=settings.AUTH_USER_MODEL)),
            ],
            options={"unique_together": {("user", "lesson")}},
        ),
        migrations.CreateModel(
            name="CardReview",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("status", models.CharField(choices=[("new", "New"), ("learning", "Learning"), ("known", "Known")], default="new", max_length=16)),
                ("last_reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("next_due_at", models.DateTimeField(blank=True, null=True)),
                ("streak", models.PositiveIntegerField(default=0)),
                ("card", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reviews", to="learning.card")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="card_reviews", to=settings.AUTH_USER_MODEL)),
            ],
            options={"unique_together": {("user", "card")}},
        ),
    ]
