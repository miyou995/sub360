# Forms for the accounts app.

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm as DjangoAuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _

from apps.core.abstract_forms import AbstractModelForm

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
        fields = ["email", "first_name", "last_name", "phone", "language"]

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
        fields = ["email", "first_name", "last_name", "phone", "language"]


class ProfileForm(AbstractModelForm):
    """Self-service profile edit for the logged-in user."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone", "language", "avatar"]
