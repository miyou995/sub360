# Views for the companies app.

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django_htmx.http import HttpResponseClientRedirect

from apps.companies.forms import (
    OnboardingActivityForm,
    OnboardingCompanyForm,
    OnboardingProfileForm,
    ReferenceFormSet,
)
from apps.subcontractors.models import Subcontractor, SubcontractorProfile

ONBOARDING_STEPS = [
    {
        "number": 1,
        "title": _("Entreprise"),
        "description": _("Coordonnées de votre siège"),
    },
    {
        "number": 2,
        "title": _("Activité"),
        "description": _("Branches, effectif et WIR"),
    },
    {"number": 3, "title": _("Profil"), "description": _("Présentation et photos")},
    {"number": 4, "title": _("Références"), "description": _("Vos projets réalisés")},
]


def get_user_subcontractor(user) -> Subcontractor:
    """Resolve the subcontractor dossier of the logged-in user or deny access."""
    profile = (
        SubcontractorProfile.objects.select_related("subcontractor__company")
        # .filter(user_id=user.pk)
        .first()
    )
    if profile is None:
        raise PermissionDenied(_("Cette page est réservée aux sous-traitants."))
    return profile.subcontractor


class SubcontractorOnboardingView(View):
    """One view, four steps; the ``step`` URL kwarg selects the form."""

    template_name = "companies/onboarding/onboarding.html"
    partial_template_name = "companies/onboarding/onboarding_step_partial.html"
    total_steps = len(ONBOARDING_STEPS)

    def dispatch(self, request, *args, **kwargs):
        self.step = kwargs.get("step", 1)
        if not 1 <= self.step <= self.total_steps:
            raise Http404
        self.subcontractor = get_user_subcontractor(request.user)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.render_step(request, self.get_form())

    def post(self, request, *args, **kwargs):
        form = self.get_form(data=request.POST, files=request.FILES)
        if form.is_valid():
            self.save_step(form)
            return self.next_step_response(request)
        return self.render_step(request, form, status=400)

    def get_form(self, data=None, files=None):
        if self.step == 1:
            return OnboardingCompanyForm(
                data=data, files=files, instance=self.subcontractor.company
            )
        if self.step == 2:
            return OnboardingActivityForm(
                data=data, files=files, instance=self.subcontractor
            )
        if self.step == 3:
            return OnboardingProfileForm(
                data=data, files=files, instance=self.subcontractor
            )
        return ReferenceFormSet(
            data=data,
            files=files,
            queryset=self.subcontractor.references.all(),
            prefix="references",
        )

    def save_step(self, form) -> None:
        if self.step == self.total_steps:
            saved_references = form.save()
            self.subcontractor.references.add(*saved_references)
        else:
            form.save()

    def next_step_response(self, request):
        if self.step >= self.total_steps:
            url = reverse("companies:onboarding_subcontractor_finish")
        else:
            url = reverse(
                "companies:onboarding_subcontractor", kwargs={"step": self.step + 1}
            )
        if getattr(request, "htmx", False):
            return HttpResponseClientRedirect(url)
        return redirect(url)

    def render_step(self, request, form, status: int = 200):
        template = (
            self.partial_template_name
            if getattr(request, "htmx", False)
            else self.template_name
        )
        context = {
            "form": form,
            "steps": ONBOARDING_STEPS,
            "step": self.step,
            "total_steps": self.total_steps,
            "is_last_step": self.step == self.total_steps,
            "subcontractor": self.subcontractor,
            "step_template": f"companies/onboarding/step_{self.step}_partial.html",
        }
        return render(request, template, context, status=status)


def onboarding_subcontractor_finish(request):
    """Close the wizard with a success message."""
    get_user_subcontractor(request.user)
    messages.success(request, _("Bienvenue ! Votre profil sous-traitant est en ligne."))
    return redirect(settings.LOGIN_REDIRECT_URL)
