# Filters for the tenders app.

import django_filters
from django.utils.translation import gettext_lazy as _

from apps.companies.models import SwissCanton
from apps.core.abstract_forms import AbstractFilterForm

from .models import Tender, TenderProcedure, TenderStatus


class TenderFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr="icontains", label=_("Titre"))
    status = django_filters.ChoiceFilter(choices=TenderStatus.choices, label=_("Statut"))
    procedure = django_filters.ChoiceFilter(choices=TenderProcedure.choices, label=_("Procédure"))
    canton = django_filters.ChoiceFilter(choices=SwissCanton.choices, label=_("Canton"))

    class Meta:
        model = Tender
        form = AbstractFilterForm
        fields = ("title", "status", "procedure", "canton", "owner")
