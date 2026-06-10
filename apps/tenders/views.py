# Views for the tenders app.
from django.utils.translation import gettext_lazy as _
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from apps.core.mixins import (
    BaseManageHtmxPageFormView,
    BreadcrumbMixin,
    DeleteMixinHTMX,
)
from django.views.generic import DetailView, TemplateView
from apps.companies.models import SwissCanton
from .filters import TenderFilter
from .forms import TenderForm
from .models import Tender, TenderStatus
from .tables import TenderTable

class TenderListView(TemplateView):
    model = Tender
    filterset_class = TenderFilter
    template_name = "tender_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = (
            Tender.objects.select_related("owner")
            .prefetch_related("execution_type", "branch")
            .all()
        )
        tender_filter = self.filterset_class(self.request.GET, queryset=queryset)
        context["tenders"] = tender_filter.qs
        return context


class TenderManageView(BreadcrumbMixin, BaseManageHtmxPageFormView):
    model = Tender
    form_class = TenderForm


class TenderDeleteView(DeleteMixinHTMX):
    model = Tender


class TenderDetailView(DetailView):
    model = Tender
    template_name = "tender_detail.html"
    context_object_name = "tender"

