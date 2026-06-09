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


class ClientProfileCreationForm(AbstractModelForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
    )
    first_name = forms.CharField(
        label=_("Prénom"),
        max_length=30,
    )
    last_name = forms.CharField(
        label=_("Nom"),
        max_length=150,
    )
    phone = forms.CharField(
        label=_("Téléphone"),
        max_length=30,
        required=False,
    )
    password1 = forms.CharField(
        label=_("Mot de passe"),
        widget=PasswordMeterWidget(attrs={"autocomplete": "new-password"}),
        strip=False,
    )
    password2 = forms.CharField(
        label=_("Confirmation du mot de passe"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
    )
    is_active = forms.BooleanField(
        label=_("Actif"),
        required=False,
        initial=True,
    )
    class Meta:
        model = ClientProfile
        fields = (
            'email',
            'first_name',
            'last_name',
            'phone',
            'is_company_admin',
            'is_active',
            'password1',
            'password2',
        )
        field_classes = {'email': UsernameField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.request and self.request.user.is_superuser:
            self.fields.pop('is_active', None)

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()

        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(_("Cet email est déjà utilisé."))

        return email

    def save(self, commit=True):
        email = self.cleaned_data["email"].strip().lower()
        user = User.objects.create_user(
            email=email,
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            is_active=self.cleaned_data.get("is_active", True),
        )

        instance = super().save(commit=False)
        instance.user = user
        instance.company = self.request.user.client_profile.company
        instance.save()
        return instance

     


class ClientProfileUpdateForm(ClientProfileCreationForm):
    class Meta(DjangoUserChangeForm.Meta):
        model = ClientProfile
        fields = (
            'email',
            'first_name',
            'last_name',
            'phone',
            'is_active',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.request and not self.request.user.is_superuser and self.request.user.has_perm(
            'users.change_user'
        ):
            self.fields.pop('is_active', None)
