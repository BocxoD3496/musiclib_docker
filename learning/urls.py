from django.urls import path
from . import views
from . import quiz_views

app_name = "learning"

urlpatterns = [
    path("", views.home, name="home"),
    path("languages/<str:language_code>/", views.lessons_list, name="lessons_list"),
    path("lessons/<int:lesson_id>/", views.lesson_detail, name="lesson_detail"),
    path("lessons/<int:lesson_id>/practice/", views.practice, name="practice"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("lessons/<int:lesson_id>/reset/", views.reset_lesson_progress, name="reset_lesson_progress"),
    path("lessons/<int:lesson_id>/quiz/", quiz_views.quiz_start, name="quiz_start"),
    path("lessons/<int:lesson_id>/quiz/<int:question_id>/", quiz_views.quiz_question, name="quiz_question"),
    path("lessons/<int:lesson_id>/quiz/<int:question_id>/answer/", quiz_views.quiz_answer, name="quiz_answer"),
    path("lessons/<int:lesson_id>/quiz/result/", quiz_views.quiz_result, name="quiz_result"),
    path("lessons/<int:lesson_id>/quiz/reset/", quiz_views.quiz_reset, name="quiz_reset"),
]
