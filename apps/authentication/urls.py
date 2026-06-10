from django.urls import path

from .views import (
    ClientSignupView,
    DeleteUser,
    LoginView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
    ProfileUpdateView,
    SignupChoiceView,
    SubcontractorSignupView,
    UserDetailView,
    UserListView,
    change_password,
    logout_view,
)

app_name = "users"

urlpatterns = [
    # Auth
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    # Password reset
    path(
        "password/reset/",
        PasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password/reset/done/",
        PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "password/reset/confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password/reset/complete/",
        PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    # Password change (logged in)
    path("users/change_password/<int:pk>/", change_password, name="change_password"),
    # Profile
    path("user/list/", UserListView.as_view(), name="list_user"),
    path("user/detail/<int:pk>/", UserDetailView.as_view(), name="user_detail"),
    path("profile/create/", ProfileUpdateView.as_view(), name="create_user"),
    path("profile/update/<int:pk>/", ProfileUpdateView.as_view(), name="update_user"),
    path("profile/delete/<int:pk>/", DeleteUser.as_view(), name="delete_user"),
    # Signup
    path("signup/", SignupChoiceView.as_view(), name="signup"),
    path("signup/client/", ClientSignupView.as_view(), name="signup_client"),
    path(
        "signup/sous-traitant/",
        SubcontractorSignupView.as_view(),
        name="signup_subcontractor",
    ),
]
