import json

from django.http import HttpResponse
from django.views.generic import ListView

from apps.clients.forms import ClientProfileCreationForm
from apps.clients.models import ClientProfile
from apps.core.mixins.form_views import BaseManageHtmxFormView


class ManageClientProfileHTMX(BaseManageHtmxFormView):
    form_class = ClientProfileCreationForm
    model = ClientProfile

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponse(
            status=204,
            headers={
                "HX-Trigger": json.dumps(
                    {
                        "closeModal": "kt_modal",
                        "refresh_table": None,
                    }
                )
            },
        )


class ClientListView(ListView):
    model = ClientProfile
    template_name = "client_list.html"
    # context_object_name = "clients"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clients = ClientProfile.objects.filter(
            company=self.request.user.client_profile.company
        ).exclude(pk=self.request.user.pk)
        context["clients"] = clients
        print("clients\n \n ----->", context["clients"])
        return context
