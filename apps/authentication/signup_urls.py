from django.urls import path

from apps.authentication.views import (
    ClientSignupView,
    SignupChoiceView,
    SubcontractorSignupView,
)

app_name = "authentication"

urlpatterns = [
    path("signup/", SignupChoiceView.as_view(), name="signup"),
    path("signup/client/", ClientSignupView.as_view(), name="signup_client"),
    path(
        "signup/sous-traitant/",
        SubcontractorSignupView.as_view(),
        name="signup_subcontractor",
    ),
]
