from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path(
        "password-reset/",
        views.password_reset_placeholder,
        name="password_reset",
    ),
    path("profile/", views.profile, name="profile"),
    path(
        "password-change/",
        views.ProfilePasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "password-change/done/",
        views.ProfilePasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
]
