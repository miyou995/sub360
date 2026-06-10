# Forms for the companies app.

from django import forms
from django.forms import modelformset_factory
from django.utils.translation import gettext_lazy as _

from apps.core.abstract_forms import AbstractModelForm
from apps.subcontractors.models import Reference, Subcontractor

from .models import Company

INPUT = "form-control form-control-solid"
SELECT = "form-select form-select-solid"


class OnboardingCompanyForm(AbstractModelForm):
    """Step 1 — head office details of the subcontractor's company."""

    class Meta:
        model = Company
        fields = ["address", "zip_code", "city", "canton", "phone", "website"]
        widgets = {
            "address": forms.TextInput(
                attrs={"class": INPUT, "placeholder": _("Rue et numéro")}
            ),
            "zip_code": forms.TextInput(
                attrs={"class": INPUT, "placeholder": _("NPA")}
            ),
            "city": forms.TextInput(
                attrs={"class": INPUT, "placeholder": _("Localité")}
            ),
            "canton": forms.Select(attrs={"class": SELECT}),
            "phone": forms.TextInput(attrs={"class": INPUT, "placeholder": "+41 ..."}),
            "website": forms.URLInput(
                attrs={"class": INPUT, "placeholder": "https://"}
            ),
        }


class OnboardingActivityForm(AbstractModelForm):
    """Step 2 — branches, headcount, company age and WIR acceptance."""

    class Meta:
        model = Subcontractor
        fields = ["branch", "worker_count", "company_age", "accepts_wir"]
        widgets = {
            "branch": forms.SelectMultiple(
                attrs={
                    "class": SELECT,
                    "data-control": "select2",
                    "data-placeholder": _("Sélectionnez vos branches"),
                    "data-close-on-select": "false",
                }
            ),
            "worker_count": forms.Select(attrs={"class": SELECT}),
            "company_age": forms.Select(attrs={"class": SELECT}),
            "accepts_wir": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class OnboardingProfileForm(AbstractModelForm):
    """Step 3 — public profile: photos, location and introduction."""

    class Meta:
        model = Subcontractor
        fields = ["profile_photo", "cover_photo", "location", "introduction"]
        widgets = {
            "profile_photo": forms.ClearableFileInput(
                attrs={"class": INPUT, "accept": "image/*"}
            ),
            "cover_photo": forms.ClearableFileInput(
                attrs={"class": INPUT, "accept": "image/*"}
            ),
            "location": forms.TextInput(
                attrs={"class": INPUT, "placeholder": _("Ex: Lausanne et région")}
            ),
            "introduction": forms.Textarea(
                attrs={
                    "class": INPUT,
                    "rows": 5,
                    "placeholder": _(
                        "Présentez votre entreprise en quelques lignes..."
                    ),
                }
            ),
        }


class ReferenceForm(AbstractModelForm):
    """Step 4 — a single reference / past project entry."""

    class Meta:
        model = Reference
        fields = ["title", "description", "start_date", "end_date"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": INPUT, "placeholder": _("Titre du projet")}
            ),
            "description": forms.Textarea(attrs={"class": INPUT, "rows": 3}),
            "start_date": forms.DateInput(attrs={"class": INPUT, "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": INPUT, "type": "date"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if start_date and end_date and end_date < start_date:
            self.add_error(
                "end_date",
                _("La date de fin doit être postérieure à la date de début."),
            )
        return cleaned_data


ReferenceFormSet = modelformset_factory(
    Reference, form=ReferenceForm, extra=1, can_delete=True
)
