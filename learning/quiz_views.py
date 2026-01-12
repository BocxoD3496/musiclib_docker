from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Lesson, QuizQuestion, QuizChoice, UserQuizAttempt

@login_required
def quiz_start(request, lesson_id: int):
    lesson = get_object_or_404(Lesson, pk=lesson_id)

    # только опубликованные вопросы
    questions = QuizQuestion.objects.filter(lesson=lesson, is_published=True).order_by("order")

    if not questions.exists():
        messages.info(request, "Пока нет опубликованных тестовых вопросов. Ждём модерацию админа.")
        return redirect("learning:lesson_detail", lesson_id=lesson.pk)

    # найдём первый вопрос, который пользователь ещё не ответил
    answered_ids = set(UserQuizAttempt.objects.filter(user=request.user, question__lesson=lesson).values_list("question_id", flat=True))
    next_q = None
    for q in questions:
        if q.id not in answered_ids:
            next_q = q
            break

    if next_q is None:
        messages.success(request, "Тест по уроку завершён ✅")
        return redirect("learning:quiz_result", lesson_id=lesson.pk)

    return redirect("learning:quiz_question", lesson_id=lesson.pk, question_id=next_q.pk)

@login_required
def quiz_question(request, lesson_id: int, question_id: int):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    q = get_object_or_404(QuizQuestion, pk=question_id, lesson=lesson, is_published=True)
    choices = q.choices.all()

    # прогресс
    total = QuizQuestion.objects.filter(lesson=lesson, is_published=True).count()
    answered = UserQuizAttempt.objects.filter(user=request.user, question__lesson=lesson).count()

    # если уже отвечал — показываем результат на этой же странице
    attempt = UserQuizAttempt.objects.filter(user=request.user, question=q).select_related("choice").first()

    return render(request, "learning/quiz_question.html", {
        "lesson": lesson,
        "question": q,
        "choices": choices,
        "attempt": attempt,
        "total": total,
        "answered": answered,
    })

@require_POST
@login_required
def quiz_answer(request, lesson_id: int, question_id: int):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    q = get_object_or_404(QuizQuestion, pk=question_id, lesson=lesson, is_published=True)

    choice_id = request.POST.get("choice_id")
    choice = get_object_or_404(QuizChoice, pk=choice_id, question=q)

    is_correct = bool(choice.is_correct)

    # сохраняем попытку (у каждого пользователя своё)
    UserQuizAttempt.objects.update_or_create(
        user=request.user,
        question=q,
        defaults={"choice": choice, "is_correct": is_correct},
    )

    if is_correct:
        messages.success(request, "Верно ✅")
    else:
        messages.error(request, "Неверно ❌")

    return redirect("learning:quiz_question", lesson_id=lesson.pk, question_id=q.pk)

@login_required
def quiz_result(request, lesson_id: int):
    lesson = get_object_or_404(Lesson, pk=lesson_id)

    total = QuizQuestion.objects.filter(lesson=lesson, is_published=True).count()
    correct = UserQuizAttempt.objects.filter(user=request.user, question__lesson=lesson, is_correct=True).count()
    wrong = UserQuizAttempt.objects.filter(user=request.user, question__lesson=lesson, is_correct=False).count()

    return render(request, "learning/quiz_result.html", {
        "lesson": lesson,
        "total": total,
        "correct": correct,
        "wrong": wrong,
    })

@login_required
def quiz_reset(request, lesson_id: int):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    UserQuizAttempt.objects.filter(user=request.user, question__lesson=lesson).delete()
    messages.info(request, "Результаты теста сброшены.")
    return redirect("learning:lesson_detail", lesson_id=lesson.pk)
