# Views for the users app.
import json
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_not_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import (
    LoginView as DjangoLoginView,
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
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.utils import translation
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from django_tables2.export import ExportMixin

from apps.authentication.filters import UserFilterSet
from apps.authentication.tables import UserHTMxTable
from apps.core.mixins import BreadcrumbMixin
from apps.core.mixins.delete_views import DeleteMixinHTMX
from apps.core.mixins.form_views import BaseManageHtmxFormView

from .forms import AuthenticationForm, ChangePasswordForm, ProfileForm

logger = logging.getLogger(__name__)

User = get_user_model()


@method_decorator(login_not_required, name="dispatch")
class LoginView(DjangoLoginView):
    template_name = "accounts/login.html"
    form_class = AuthenticationForm
    redirect_authenticated_user = True

    def form_invalid(self, form):
        print("form invalid, errors:", form.errors)
        messages.error(self.request, _("Email ou mot de passe incorrect."))
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        print("form valid, user:", form.get_user())
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


# class PasswordChangeDoneView(DjangoPasswordChangeDoneView):
#     template_name = "registration/password_change_done.html"


@permission_required("users.change_user", raise_exception=True)
def change_password(request, pk):
    context = {}
    template_name = "accounts/snippets/change_password.html"
    user = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        user_form = ChangePasswordForm(request.POST, instance=user)
        if user_form.is_valid():
            cd = user_form.cleaned_data
            password = cd["password"]
            password2 = cd["password2"]
            if password == password2:
                user.set_password(password)
                user.is_active = True
                user.save()
                messages.success(request, _("Mot de passe modifié avec succès"))
                return HttpResponse(
                    status=200,
                    headers={
                        "HX-Trigger": json.dumps(
                            {
                                "closeModal": None,
                                "redirect_to": reverse("users:list_user"),
                            }
                        )
                    },
                )
            else:
                messages.error(request, _("Formulaire invalide"))
        else:
            # messages.error(request, _('Formulaire invalide - vérifier les erreurs ci-dessous.'))
            context["form"] = ChangePasswordForm(data=request.POST or None)
            context["c_user"] = user
            return render(
                request,
                template_name=template_name,
                context=context,
            )
    else:
        user_form = ChangePasswordForm()
    context = {"form": user_form, "c_user": user}
    return render(request, template_name, context)


# --------------------------------------------------------------------------- #
# Profile
# --------------------------------------------------------------------------- #


class UserListView(
    BreadcrumbMixin, PermissionRequiredMixin, SingleTableMixin, ExportMixin, FilterView
):
    permission_required = "users.view_user"
    model = User
    table_class = UserHTMxTable
    paginate_by = 8
    filterset_class = UserFilterSet

    def get_queryset(self):
        queryset = User.objects.limit_user(self.request.user).all()
        filters = self.filterset_class(self.request.GET, queryset=queryset)
        return filters.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # context['bulk_delete_url'] = self.model.get_bulk_delete_url()
        context["model"] = self.model
        return context

    def get_template_names(self) -> list[str]:
        if self.request.htmx:
            return ["tables/table_partial.html"]
        return ["accounts/user_list.html"]


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    context_object_name = "profile_user"
    template_name = "accounts/user_detail.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object

        client_profile = getattr(user, "client_profile", None)
        subcontractor_profile = getattr(user, "subcontractor_profile", None)

        team = []
        projects = []
        references = []
        company = None
        role_label = None

        if client_profile:
            company = client_profile.company
            role_label = (
                _("Administrateur") if client_profile.is_company_admin else _("Client")
            )
            team = (
                User.objects.filter(client_profile__company=company)
                .exclude(pk=user.pk)
                .select_related("client_profile")
            )
            projects = company.tenders.all()
        elif subcontractor_profile:
            subcontractor = subcontractor_profile.subcontractor
            company = subcontractor.company
            role_label = _("Sous-traitant")
            team = (
                User.objects.filter(subcontractor_profile__subcontractor=subcontractor)
                .exclude(pk=user.pk)
                .select_related("subcontractor_profile")
            )
            projects = subcontractor.applications.select_related("tender").all()
            references = subcontractor.references.prefetch_related("images")

        context.update(
            {
                "client_profile": client_profile,
                "subcontractor_profile": subcontractor_profile,
                "company": company,
                "role_label": role_label,
                "team": team,
                "projects": projects,
                "references": references,
            }
        )
        return context


class ProfileUpdateView(BaseManageHtmxFormView):
    required_permission = "users.change_user"
    model = User
    form_class = ProfileForm


class DeleteUser(DeleteMixinHTMX):
    permission_required = "users.delete_user"
    model = User
