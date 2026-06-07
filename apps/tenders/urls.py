from django.urls import path

from . import views

app_name = "tenders"

urlpatterns = [
    path("", views.TenderListView.as_view(), name="list_tender"),
    path("create/", views.TenderManageView.as_view(), name="create_tender"),
    path("<int:pk>/update/", views.TenderManageView.as_view(), name="update_tender"),
    path("<int:pk>/delete/", views.TenderDeleteView.as_view(), name="delete_tender"),
]
