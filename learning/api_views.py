from rest_framework import permissions, viewsets
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Language, Lesson, Card, UserLessonProgress
from .serializers import LanguageSerializer, LessonSerializer, CardSerializer, UserLessonProgressSerializer

class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Language.objects.all().order_by("name")
    serializer_class = LanguageSerializer
    permission_classes = [permissions.AllowAny]

class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Lesson.objects.select_related("language").all().order_by("language__name", "order")
    serializer_class = LessonSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        lang_code = self.request.query_params.get("language")
        q = self.request.query_params.get("q")
        if lang_code:
            qs = qs.filter(language__code=lang_code)
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
        return qs

class CardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Card.objects.select_related("lesson", "lesson__language").all()
    serializer_class = CardSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        lang_code = self.request.query_params.get("language")
        q = self.request.query_params.get("q")
        if lang_code:
            qs = qs.filter(language__code=lang_code)
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
        return qs

class ProgressViewSet(viewsets.ModelViewSet):
    """Authenticated REST API for a user's progress."""
    serializer_class = UserLessonProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserLessonProgress.objects.filter(user=self.request.user).select_related("lesson")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        total = qs.count()
        completed = qs.filter(completed=True).count()
        return Response({"total": total, "completed": completed})
