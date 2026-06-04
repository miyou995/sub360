# Views for the users app.

import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView as DjangoLoginView,
)
from django.contrib.auth.views import (
    PasswordChangeDoneView as DjangoPasswordChangeDoneView,
)
from django.contrib.auth.views import (
    PasswordChangeView as DjangoPasswordChangeView,
)
from django.contrib.auth.views import (
    PasswordResetCompleteView as DjangoPasswordResetCompleteView,
)
from django.contrib.auth.views import (
    PasswordResetConfirmView as DjangoPasswordResetConfirmView,
)
from django.contrib.auth.views import (
    PasswordResetDoneView as DjangoPasswordResetDoneView,
)
from django.contrib.auth.views import (
    PasswordResetView as DjangoPasswordResetView,
)
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import translation
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, UpdateView

from .forms import AuthenticationForm, ProfileForm

logger = logging.getLogger(__name__)

User = get_user_model()


@method_decorator(login_not_required, name="dispatch")
class LoginView(DjangoLoginView):
    template_name = "accounts/login.html"
    form_class = AuthenticationForm
    redirect_authenticated_user = True

    def form_invalid(self, form):
        messages.error(self.request, _("Email ou mot de passe incorrect."))
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        auth_login(self.request, form.get_user())
        remember_me = self.request.POST.get("remember_me")
        if remember_me:
            self.request.session.set_expiry(settings.SESSION_COOKIE_AGE)
        else:
            self.request.session.set_expiry(0)

        user_language = self.request.user.language or "fr"
        translation.activate(user_language)
        response = HttpResponseRedirect(self.get_success_url())
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, user_language)
        return response


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("users:login"))


# --------------------------------------------------------------------------- #
# Password reset / change
# --------------------------------------------------------------------------- #
@method_decorator(login_not_required, name="dispatch")
class PasswordResetView(DjangoPasswordResetView):
    template_name = "registration/password_reset_form.html"
    email_template_name = "registration/password_reset_email_custom.html"
    subject_template_name = "registration/password_reset_subject_custom.txt"
    success_url = reverse_lazy("users:password_reset_done")


@method_decorator(login_not_required, name="dispatch")
class PasswordResetDoneView(DjangoPasswordResetDoneView):
    template_name = "registration/password_reset_done.html"


@method_decorator(login_not_required, name="dispatch")
class PasswordResetConfirmView(DjangoPasswordResetConfirmView):
    template_name = "registration/password_reset_confirm.html"
    success_url = reverse_lazy("users:password_reset_complete")


@method_decorator(login_not_required, name="dispatch")
class PasswordResetCompleteView(DjangoPasswordResetCompleteView):
    template_name = "registration/password_reset_complete.html"


class PasswordChangeView(DjangoPasswordChangeView):
    template_name = "registration/password_change_form.html"
    success_url = reverse_lazy("users:password_change_done")


class PasswordChangeDoneView(DjangoPasswordChangeDoneView):
    template_name = "registration/password_change_done.html"


# --------------------------------------------------------------------------- #
# Profile
# --------------------------------------------------------------------------- #
class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    context_object_name = "profile_user"
    template_name = "accounts/profile.html"

    def get_object(self, queryset=None):
        return self.request.user


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = "accounts/profile_form.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, _("Profil mis à jour avec succès."))
        return super().form_valid(form)
