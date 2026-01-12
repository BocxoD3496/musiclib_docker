from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import LessonSearchForm
from .models import Card, CardReview, Language, Lesson, UserLessonProgress, UserQuizAttempt
from .services import next_due_for_result

def home(request):
    # Public page (Guest can view)
    languages = Language.objects.all().order_by("name")
    return render(request, "learning/home.html", {"languages": languages})

def lessons_list(request, language_code: str):
    language = get_object_or_404(Language, code=language_code)
    form = LessonSearchForm(request.GET or None)

    qs = (
        Lesson.objects
        .filter(language=language)
        .annotate(
            quiz_published_count=Count("quiz_questions", filter=Q(quiz_questions__is_published=True))
        )
    )

    if form.is_valid():
        q = form.cleaned_data.get("q") or ""
        if q.strip():
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

        sort = form.cleaned_data.get("sort") or "order"
        if sort == "title":
            qs = qs.order_by("title")
        elif sort == "updated":
            qs = qs.order_by("-updated_at")
        else:
            qs = qs.order_by("order")

    return render(request, "learning/lessons_list.html", {
        "language": language,
        "lessons": qs,
        "form": form
    })

def lesson_detail(request, lesson_id: int):
    lesson = get_object_or_404(Lesson, pk=lesson_id)

    # Cards
    total_cards = lesson.cards.count()

    # Quiz (published only)
    quiz_total = lesson.quiz_questions.filter(is_published=True).count()

    quiz_correct = 0
    quiz_wrong = 0
    quiz_answered = 0

    if request.user.is_authenticated and quiz_total > 0:
        attempts = UserQuizAttempt.objects.filter(
            user=request.user,
            question__lesson=lesson,
            question__is_published=True,
        )
        quiz_answered = attempts.count()
        quiz_correct = attempts.filter(is_correct=True).count()
        quiz_wrong = attempts.filter(is_correct=False).count()

    # Cards progress (saved only for auth users)
    progress = None
    if request.user.is_authenticated:
        progress, _ = UserLessonProgress.objects.get_or_create(user=request.user, lesson=lesson)

    return render(request, "learning/lesson_detail.html", {
        "lesson": lesson,
        "total_cards": total_cards,
        "progress": progress,

        # quiz stats for template
        "quiz_total": quiz_total,
        "quiz_answered": quiz_answered,
        "quiz_correct": quiz_correct,
        "quiz_wrong": quiz_wrong,
    })

    lesson = get_object_or_404(Lesson, pk=lesson_id)

    total_cards = lesson.cards.count()

    # --- QUIZ stats (published only) ---
    quiz_total = lesson.quiz_questions.filter(is_published=True).count()

    quiz_correct = 0
    quiz_wrong = 0
    quiz_answered = 0

    if request.user.is_authenticated and quiz_total > 0:
        attempts = UserQuizAttempt.objects.filter(
            user=request.user,
            question__lesson=lesson,
            question__is_published=True
        )
        quiz_answered = attempts.count()
        quiz_correct = attempts.filter(is_correct=True).count()
        quiz_wrong = attempts.filter(is_correct=False).count()

    # --- Cards progress (your existing logic) ---
    progress = None
    if request.user.is_authenticated:
        progress, _ = UserLessonProgress.objects.get_or_create(user=request.user, lesson=lesson)

    return render(request, "learning/lesson_detail.html", {
        "lesson": lesson,
        "total_cards": total_cards,
        "progress": progress,

        # quiz in template
        "quiz_total": quiz_total,
        "quiz_answered": quiz_answered,
        "quiz_correct": quiz_correct,
        "quiz_wrong": quiz_wrong,
    })


def _get_next_card_for_session(lesson: Lesson, index: int):
    cards = list(lesson.cards.all())
    if not cards:
        return None, 0, 0
    if index >= len(cards):
        return None, index, len(cards)
    return cards[index], index, len(cards)

def practice(request, lesson_id: int):
    lesson = get_object_or_404(Lesson, pk=lesson_id)

    # Guests can practice, but progress will not be saved to DB.
    is_guest = not request.user.is_authenticated

    if is_guest:
        session_key = f"guest_lesson_{lesson.pk}_index"
        index = int(request.session.get(session_key, 0))
    else:
        progress, _ = UserLessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
        index = progress.current_index

    card, index, total = _get_next_card_for_session(lesson, index)

    if total == 0:
        messages.info(request, "В этом уроке пока нет карточек.")
        return redirect("learning:lesson_detail", lesson_id=lesson.pk)

    if card is None:
        # Finished
        if is_guest:
            request.session.pop(session_key, None)
            messages.success(request, "Урок пройден! Чтобы сохранить прогресс — войдите или зарегистрируйтесь.")
            return redirect("learning:lesson_detail", lesson_id=lesson.pk)
        else:
            progress.completed = True
            progress.current_index = total
            progress.save(update_fields=["completed", "current_index", "updated_at"])
            messages.success(request, "Урок пройден! Прогресс сохранён.")
            return redirect("learning:dashboard")

    if request.method == "POST":
        action = request.POST.get("action")
        # Basic input handling (avoid trusting arbitrary values)
        if action not in {"known", "unknown"}:
            messages.error(request, "Некорректное действие.")
            return redirect("learning:practice", lesson_id=lesson.pk)

        is_correct = action == "known"

        # Update session/DB progress
        if is_guest:
            # Guests: only session progress
            if is_correct:
                request.session[f"guest_lesson_{lesson.pk}_correct"] = int(request.session.get(f"guest_lesson_{lesson.pk}_correct", 0)) + 1
            else:
                request.session[f"guest_lesson_{lesson.pk}_wrong"] = int(request.session.get(f"guest_lesson_{lesson.pk}_wrong", 0)) + 1
            request.session[session_key] = index + 1
        else:
            if is_correct:
                progress.correct += 1
            else:
                progress.wrong += 1
            progress.current_index = index + 1
            progress.save()

            # Also keep per-card review info (simple "SRS")
            review, _ = CardReview.objects.get_or_create(user=request.user, card=card)
            streak, next_due = next_due_for_result(is_correct, review.streak)
            review.streak = streak
            review.status = "known" if streak >= 3 else ("learning" if streak > 0 else "learning")
            review.last_reviewed_at = timezone.now()
            review.next_due_at = next_due
            review.save()

        return redirect("learning:practice", lesson_id=lesson.pk)

    # GET
    guest_note = None
    if is_guest:
        guest_note = "Гостевой режим: прогресс не сохраняется. Войдите, чтобы сохранять прогресс и видеть статистику."

    return render(request, "learning/practice.html", {
        "lesson": lesson,
        "card": card,
        "index": index,
        "total": total,
        "is_guest": is_guest,
        "guest_note": guest_note,
    })

@login_required
def dashboard(request):
    lessons = (
        Lesson.objects
        .annotate(
            quiz_total=Count("quiz_questions", filter=Q(quiz_questions__is_published=True))
        )
        .filter(quiz_total__gt=0)
        .order_by("language__code", "order")
    )

    attempts = UserQuizAttempt.objects.filter(
        user=request.user,
        question__is_published=True,
    ).select_related("question", "question__lesson", "question__lesson__language")

    stats = {}
    for a in attempts:
        lid = a.question.lesson_id
        if lid not in stats:
            stats[lid] = {"correct": 0, "wrong": 0, "answered": 0}
        stats[lid]["answered"] += 1
        if a.is_correct:
            stats[lid]["correct"] += 1
        else:
            stats[lid]["wrong"] += 1

    rows = []
    for lesson in lessons:
        s = stats.get(lesson.id, {"correct": 0, "wrong": 0, "answered": 0})
        completed = s["answered"] >= lesson.quiz_total

        rows.append({
            "language_code": lesson.language.code,
            "lesson_id": lesson.id,
            "lesson_title": lesson.title,
            "correct": s["correct"],
            "wrong": s["wrong"],
            "answered": s["answered"],
            "total": lesson.quiz_total,
            "completed": completed,
        })

    return render(request, "learning/dashboard.html", {"rows": rows})

@login_required
def reset_lesson_progress(request, lesson_id: int):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    UserLessonProgress.objects.filter(user=request.user, lesson=lesson).update(
        current_index=0, correct=0, wrong=0, completed=False
    )
    CardReview.objects.filter(user=request.user, card__lesson=lesson).delete()
    messages.success(request, "Прогресс урока сброшен.")
    return redirect("learning:lesson_detail", lesson_id=lesson.pk)
