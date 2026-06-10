from django.urls import path
from django.views.generic import RedirectView

from apps.companies.views import (
    SubcontractorOnboardingView,
    onboarding_subcontractor_finish,
)

app_name = "companies"

urlpatterns = [
    path(
        "onboarding/sous-traitant/",
        RedirectView.as_view(pattern_name="companies:onboarding_subcontractor"),
        {"step": 1},
        name="onboarding_subcontractor_start",
    ),
    path(
        "onboarding/sous-traitant/terminer/",
        onboarding_subcontractor_finish,
        name="onboarding_subcontractor_finish",
    ),
    path(
        "onboarding/sous-traitant/<int:step>/",
        SubcontractorOnboardingView.as_view(),
        name="onboarding_subcontractor",
    ),
]
