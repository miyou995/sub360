# Views for the tenders app.

from django.utils.translation import gettext_lazy as _
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from apps.core.mixins import (
    BaseManageHtmxPageFormView,
    BreadcrumbMixin,
    DeleteMixinHTMX,
)

from django.views.generic import TemplateView
from .filters import TenderFilter
from .forms import TenderForm
from .models import Tender
from .tables import TenderTable


class TenderListView(TemplateView):
    model = Tender
    table_class = TenderTable
    filterset_class = TenderFilter
    template_name = "tender_list.html"
    paginate_by = 25
    context_object_name = "tenders"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # tenders = self.filterset_class(self.request.GET, queryset=self.model.objects.select_related("owner").prefetch_related("execution_type", "branch").all())
        # context["filter"] = tenders
        # context["table"] = self.table_class(tenders.qs)
        tenders = Tender.objects.select_related("owner").prefetch_related("execution_type", "branch").all()
        context["tenders"] = tenders
        print("this is tender list view \n \n ")
        for tender in context["tenders"]:
            print("Tender:------------------->>> ", tender.title, " - ", tender.owner)
        return context
    # def get_queryset(self):
    #     return (
    #         Tender.objects.select_related("owner")
    #         .prefetch_related("execution_type", "branch")
    #         .all()
    #     )


class TenderManageView(BreadcrumbMixin, BaseManageHtmxPageFormView):
    model = Tender
    form_class = TenderForm
    # template_name = "tender_form.html"
    success_message = _("Appel d'offres enregistré avec succès.")


class TenderDeleteView(DeleteMixinHTMX):
    model = Tender
