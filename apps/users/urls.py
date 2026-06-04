from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    # Auth
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    # Password reset
    path(
        "password/reset/",
        views.PasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password/reset/done/",
        views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "password/reset/confirm/<uidb64>/<token>/",
        views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password/reset/complete/",
        views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    # Password change (logged in)
    path(
        "password/change/",
        views.PasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "password/change/done/",
        views.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    # Profile
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/edit/", views.ProfileUpdateView.as_view(), name="update_profile"),
]
