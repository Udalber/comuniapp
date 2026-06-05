from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeDoneView, PasswordChangeView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods, require_POST

from .forms import LoginForm, ProfileForm, RegisterForm

AUTH_BACKEND = settings.AUTHENTICATION_BACKENDS[0]


def _redirect_after_auth():
    return redirect("core:home")


@require_http_methods(["GET", "POST"])
def register(request):
    if request.user.is_authenticated:
        return _redirect_after_auth()

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend=AUTH_BACKEND)
            display_name = user.get_full_name() or user.first_name
            messages.success(
                request,
                f"¡Bienvenido/a a ComuniApp, {display_name}! Tu cuenta ha sido creada.",
            )
            return _redirect_after_auth()
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return _redirect_after_auth()

    form = LoginForm(request=request)
    if request.method == "POST":
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user, backend=AUTH_BACKEND)
            if not form.cleaned_data.get("remember_me"):
                request.session.set_expiry(0)
            messages.success(request, "Has iniciado sesión correctamente.")
            return _redirect_after_auth()

    return render(request, "accounts/login.html", {"form": form})


@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión.")
    return redirect("core:home")


def password_reset_placeholder(request):
    """MVP: recuperación de contraseña en sesión posterior."""
    return render(request, "accounts/password_reset_placeholder.html")


@login_required
@require_http_methods(["GET", "POST"])
def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Tu perfil ha sido actualizado.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(
            request.user,
            initial={
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "email": request.user.email,
            },
        )

    return render(request, "accounts/profile.html", {"form": form})


class ProfilePasswordChangeView(PasswordChangeView):
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("accounts:password_change_done")


class ProfilePasswordChangeDoneView(PasswordChangeDoneView):
    template_name = "accounts/password_change_done.html"
