from django.urls import path

from .views import SubcontractorListView

app_name = "subcontractors"

urlpatterns = [
    path("", SubcontractorListView.as_view(), name="list_subcontractor"),
]
