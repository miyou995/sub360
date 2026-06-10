# Forms for the accounts app.

from allauth.account.forms import SignupForm as AllauthSignupForm
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm as DjangoAuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from apps.clients.models import ClientProfile
from apps.companies.models import Company, CompanyType
from apps.core.abstract_forms import AbstractModelForm
from apps.core.widgets import PasswordMeterWidget
from apps.subcontractors.models import Subcontractor, SubcontractorProfile

User = get_user_model()


class AuthenticationForm(DjangoAuthenticationForm):
    """Email/password login form."""

    username = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(
            attrs={"autofocus": True, "class": "form-control bg-transparent"}
        ),
    )
    password = forms.CharField(
        label=_("Mot de passe"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "class": "form-control bg-transparent",
                "placeholder": _("Mot de passe"),
            }
        ),
    )


class UserCreationForm(AbstractModelForm):
    """Create a user with a password."""

    password1 = forms.CharField(
        label=_("Mot de passe"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label=_("Confirmation du mot de passe"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "phone"]

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Les mots de passe ne correspondent pas."))
        validate_password(password2, self.instance)
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserUpdateForm(AbstractModelForm):
    """Update a user without touching the password."""

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "phone"]


class ProfileForm(AbstractModelForm):
    """Self-service profile edit for the logged-in user."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone", "avatar"]


class ChangePasswordForm(AbstractModelForm):
    password2 = forms.CharField(
        label=_("Confirmer le mot de passe"),
        strip=False,
        widget=PasswordMeterWidget(
            attrs={"class": "form-control", "autocomplete": "new-password"}
        ),
    )

    class Meta:
        model = User
        fields = ("password",)
        labels = {"password": _("Nouveau mot de passe")}
        widgets = {
            "password": PasswordMeterWidget(
                attrs={"class": "form-control", "autocomplete": "new-password"}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password and password2:
            if password != password2:
                self.add_error(
                    "password2", _("Les mots de passe ne correspondent pas.")
                )
        return cleaned_data


# ---------------------------------------------------------------------------
# Signup forms (django-allauth)
# These forms are intentionally NOT AbstractModelForm subclasses: allauth's
# SignupForm already owns email/password validation and user creation.
# ---------------------------------------------------------------------------

TEXT_INPUT_CLASS = "form-control form-control-lg form-control-solid bg-transparent"
SELECT_CLASS = "form-select form-select-lg form-select-solid bg-transparent"


class MetronicSignupStyleMixin:
    """Apply Metronic input classes to every widget of an allauth form."""

    def apply_metronic_classes(self) -> None:
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, forms.Select):
                widget.attrs.setdefault("class", SELECT_CLASS)
            else:
                widget.attrs.setdefault("class", TEXT_INPUT_CLASS)
                widget.attrs.setdefault("placeholder", field.label)


class BaseRoleSignupForm(MetronicSignupStyleMixin, AllauthSignupForm):
    """Identity + company fields shared by the client and subcontractor signups."""

    company_type: str = ""  # overridden by subclasses

    first_name = forms.CharField(label=_("Prénom"), max_length=150)
    last_name = forms.CharField(label=_("Nom"), max_length=150)
    phone = forms.CharField(label=_("Téléphone"), max_length=30, required=False)
    company_name = forms.CharField(label=_("Raison sociale"), max_length=255)
    company_uid = forms.CharField(
        label=_("Numéro IDE / UID"),
        max_length=20,
        required=False,
        help_text=_("Identifiant des entreprises suisse (ex: CHE-123.456.789)."),
    )

    field_order = [
        "first_name",
        "last_name",
        "email",
        "phone",
        "company_name",
        "company_uid",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_metronic_classes()

    def clean_company_uid(self) -> str | None:
        uid = (self.cleaned_data.get("company_uid") or "").strip() or None
        if uid and Company.objects.filter(uid=uid).exists():
            raise forms.ValidationError(
                _("Une entreprise avec ce numéro IDE est déjà inscrite.")
            )
        return uid

    def save(self, request):
        with transaction.atomic():
            user = super().save(request)
            user.first_name = self.cleaned_data["first_name"]
            user.last_name = self.cleaned_data["last_name"]
            user.phone = self.cleaned_data.get("phone", "")
            user.save(update_fields=["first_name", "last_name", "phone"])

            company = Company.objects.create(
                name=self.cleaned_data["company_name"],
                company_type=self.company_type,
                uid=self.cleaned_data.get("company_uid"),
                email=user.email,
                phone=user.phone,
            )
            self.create_profile(user, company)
        return user

    def create_profile(self, user, company: Company) -> None:
        raise NotImplementedError


class ClientSignupForm(BaseRoleSignupForm):
    """Signup of a client company. The first user becomes the team admin."""

    company_type = CompanyType.CLIENT

    position = forms.CharField(label=_("Fonction"), max_length=150, required=False)

    field_order = BaseRoleSignupForm.field_order + ["position"]

    def create_profile(self, user, company: Company) -> None:
        ClientProfile.objects.create(
            user=user,
            company=company,
            position=self.cleaned_data.get("position", ""),
            is_company_admin=True,
        )


class SubcontractorSignupForm(BaseRoleSignupForm):
    """Signup of a subcontractor: one company = one dossier = one login."""

    company_type = CompanyType.SUBCONTRACTOR

    def create_profile(self, user, company: Company) -> None:
        subcontractor = Subcontractor.objects.create(company=company)
        SubcontractorProfile.objects.create(user=user, subcontractor=subcontractor)
