from django.urls import path
from .views import register_view, AppLoginView, AppLogoutView

app_name = "accounts"

urlpatterns = [
    path("register/", register_view, name="register"),
    path("login/", AppLoginView.as_view(), name="login"),
    path("logout/", AppLogoutView.as_view(), name="logout"),
]
