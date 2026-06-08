import django_filters
from django import forms
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from apps.core.abstract_forms import AbstractFilterForm
from apps.tenders.models import Branch

from .models import Subcontractor


class SubcontractorFilter(django_filters.FilterSet):
    """Sidebar filters for the client-facing subcontractor list."""

    search = django_filters.CharFilter(
        method="filter_search",
        label=_("Recherche"),
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-solid",
                "placeholder": _("Entreprise ou localisation…"),
            }
        ),
    )
    branch = django_filters.ModelChoiceFilter(
        field_name="branch",
        queryset=Branch.objects.filter(is_active=True),
        label=_("Branche"),
        empty_label=_("Toutes les branches"),
        widget=forms.Select(attrs={"class": "form-select form-select-solid"}),
    )
    worker_count = django_filters.ChoiceFilter(
        choices=Subcontractor.WorkerCount.choices,
        label=_("Nombre d'employés"),
        empty_label=_("Tous"),
        widget=forms.Select(attrs={"class": "form-select form-select-solid"}),
    )
    company_age = django_filters.ChoiceFilter(
        choices=Subcontractor.CompanyAge.choices,
        label=_("Ancienneté"),
        empty_label=_("Toutes"),
        widget=forms.Select(attrs={"class": "form-select form-select-solid"}),
    )
    has_valid_insurance = django_filters.BooleanFilter(
        field_name="has_valid_insurance",
        label=_("Assurance valide"),
        widget=django_filters.widgets.BooleanWidget(
            attrs={"class": "form-select form-select-solid"}
        ),
    )
    accepts_wir = django_filters.BooleanFilter(
        field_name="accepts_wir",
        label=_("Accepte le WIR"),
        widget=django_filters.widgets.BooleanWidget(
            attrs={"class": "form-select form-select-solid"}
        ),
    )

    class Meta:
        model = Subcontractor
        fields = (
            "search",
            "branch",
            "worker_count",
            "company_age",
            "has_valid_insurance",
            "accepts_wir",
        )
        form = AbstractFilterForm

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(company__name__icontains=value) | Q(location__icontains=value)
        )
