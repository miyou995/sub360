import logging

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import (
    UserChangeForm as DjangoUserChangeForm,
    UserCreationForm as DjangoUserCreationForm,
    UsernameField,
)
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from apps.clients.models import ClientProfile
from apps.core.abstract_forms import AbstractModelForm
from apps.core.widgets import PasswordMeterWidget

logger = logging.getLogger(__name__)

User = get_user_model()

class BaseClientProfileForm(AbstractModelForm):
    email = forms.EmailField(label=_("Email"),max_length=254,)
    first_name = forms.CharField(label=_("Prénom"),max_length=30,)
    last_name = forms.CharField(label=_("Nom"),max_length=150,)
    phone = forms.CharField(
        label=_("Téléphone"),
        max_length=30,
        required=False,
    )

    avatar = forms.ImageField(
        label=_("Photo de profil"),
        required=False,
    )

    is_active = forms.BooleanField(
        label=_("Actif"),
        required=False,
        initial=True,
    )

    class Meta:
        model = ClientProfile
        fields = (
            "email",
            "first_name",
            "last_name",
            "phone",
            "position",
            "avatar",
            "is_company_admin",
            "is_active",
        )

    def populate_user(self, user):
        user.email = self.cleaned_data["email"].strip().lower()
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.phone = self.cleaned_data["phone"]
        user.is_active = self.cleaned_data.get("is_active", True)

        if self.cleaned_data.get("avatar"):
            user.avatar = self.cleaned_data["avatar"]

        return user

class ClientProfileCreationForm(BaseClientProfileForm):
    password = forms.CharField(
        label=_("Mot de passe"),
        widget=PasswordMeterWidget(
            attrs={"autocomplete": "new-password"}
        ),
        strip=False,
    )

    password2 = forms.CharField(
        label=_("Confirmation du mot de passe"),
        widget=PasswordMeterWidget(
            attrs={"autocomplete": "new-password"}
        ),
        strip=False,
    )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(_("Cet email est déjà utilisé."))

        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password and password2 and password != password2:
            self.add_error(
                "password2",
                _("Les mots de passe ne correspondent pas."),
            )

        return cleaned_data

    def save(self, commit=True):
        user = User.objects.create_user(
            email=self.cleaned_data["email"].strip().lower(),
            password=self.cleaned_data["password"],
        )
        self.populate_user(user)

        if commit:
            user.save()
        instance = super().save(commit=False)
        instance.user = user
        instance.company = self.request.user.client_profile.company

        if commit:
            instance.save()

        return instance
    
class ClientProfileUpdateForm(BaseClientProfileForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            user = self.instance.user

            self.initial.update(
                {
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_active": user.is_active,
                    "avatar"   : user.avatar,
                    "phone"   : user.phone,
                }
            )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        qs = User.objects.filter(email__iexact=email)

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.user.pk)

        if qs.exists():
            raise ValidationError(_("Cet email est déjà utilisé."))

        return email

    def save(self, commit=True):
        instance = super().save(commit=False)
        user = self.populate_user(self.instance.user)

        if commit:
            user.save()
            instance.save()

        return instance