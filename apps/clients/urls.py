from django.urls import path

from apps.clients.views import (ClientDeleteView, ClientDetailView, ClientListView,
                                 CreateClientProfileHTMX, UpdateClientProfileHTMX)

app_name = "clients"
urlpatterns = [
    path("list/", ClientListView.as_view(), name="client_list"),
    path("create/", CreateClientProfileHTMX.as_view(), name="create_clientprofile"),
    path("update/<int:pk>/", UpdateClientProfileHTMX.as_view(), name="update_clientprofile"),
    path("detail/<int:pk>/", ClientDetailView.as_view(), name="detail_clientprofile"),
    path("<int:pk>/delete/", ClientDeleteView.as_view(), name="delete_clientprofile"),
    
    


]