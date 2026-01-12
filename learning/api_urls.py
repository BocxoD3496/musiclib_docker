from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .api_views import LanguageViewSet, LessonViewSet, CardViewSet, ProgressViewSet

router = DefaultRouter()
router.register(r"languages", LanguageViewSet, basename="language")
router.register(r"lessons", LessonViewSet, basename="lesson")
router.register(r"cards", CardViewSet, basename="card")
router.register(r"progress", ProgressViewSet, basename="progress")

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("", include(router.urls)),
]
