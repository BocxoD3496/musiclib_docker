from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from .forms import RegisterForm

def register_view(request):
    # Guests can view public pages; registration enables progress saving.
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("learning:dashboard")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})

class AppLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

class AppLogoutView(LogoutView):
    next_page = reverse_lazy("learning:home")
