"""
URL configuration for sub360 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from datetime import date

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

# admin_url = settings.ADMIN_URL

WIP_MODULES = [
    {"icon": "🏢", "label": "Clients", "desc": "Gestion des clients"},
    {"icon": "📋", "label": "Appels d'offres", "desc": "Tenders & soumissions"},
    {"icon": "📄", "label": "Documents", "desc": "GED & fichiers"},
    {"icon": "🏭", "label": "Entreprises", "desc": "Annuaire entreprises"},
    {"icon": "📊", "label": "Statistiques", "desc": "Tableaux de bord"},
    {"icon": "✅", "label": "Candidatures", "desc": "Suivi des candidatures"},
    {"icon": "⭐", "label": "Évaluations", "desc": "Notes & avis"},
    {"icon": "🔔", "label": "Notifications", "desc": "Centre de notifications"},
    {"icon": "📬", "label": "Messagerie", "desc": "Messagerie interne"},
    {"icon": "🔌", "label": "Intégrations", "desc": "API & connecteurs"},
    {"icon": "🎯", "label": "Projets", "desc": "Suivi de projets"},
    {"icon": "💳", "label": "Abonnements", "desc": "Plans & facturation"},
    {"icon": "✉️", "label": "Newsletter", "desc": "Campagnes e-mail"},
    {"icon": "🛡️", "label": "Vérification", "desc": "KYC & conformité"},
]


class DevIndexView(TemplateView):
    template_name = "dev_index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["wip_modules"] = WIP_MODULES
        ctx["today"] = date.today()
        return ctx


urlpatterns = [
    path("", DevIndexView.as_view(), name="dev_index"),
    path("accounts/", include("apps.users.urls")),
    path("tenders/", include("apps.tenders.urls")),
    path("applications/", include("apps.applications.urls")),
    path("ratings/", include("apps.ratings.urls")),
    path("companies/", include("apps.companies.urls")),
    # path("clients/", include("apps.clients.urls")),
    path("subcontractors/", include("apps.subcontractors.urls")),
    path("documents/", include("apps.documents.urls")),
    path("verification/", include("apps.verification.urls")),
    # NOTE: apps.core.urls is not wired yet — apps/core/views.py still references
    # legacy apps (billing/finance/recurrent) and must be rebuilt first.
    # path(f"{admin_url}/", admin.site.urls),
]
devpatterns = []

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    devpatterns = [
        path("admin/", admin.site.urls),
        path("schema/", include("schematic.urls")),
        path("lumen/", include("django_lumen.urls")),
    ]


urlpatterns += devpatterns
