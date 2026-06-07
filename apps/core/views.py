import logging
from datetime import date, datetime

from apps.core.mixins import BaseManageHtmxFormView, DeleteMixinHTMX

from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin


logger = logging.getLogger(__name__)


def set_language(request, language="fr"):
    lang_code = language
    translation.activate(lang_code)
    request.session[settings.LANGUAGE_SESSION_KEY] = lang_code
    request.user.language = lang_code
    request.user.save()

    response = HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
    return response


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["size_class"] = "modal-lg mw-850px"
       
        return context

    # def get_template_names(self):
    #     if self.request.htmx:
    #         return ["tables/table_partial.html"]
    #     else:
    #         return ["index.html"]


# ----------------------------------Configuration----------------------------------

