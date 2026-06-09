from django.urls import path

from apps.clients.views import ClientListView, ManageClientProfileHTMX

app_name = "clients"
urlpatterns = [
    path("clients/create/", ManageClientProfileHTMX.as_view(), name="create_clientprofile"),
    path("clients/update/<int:pk>/", ManageClientProfileHTMX.as_view(), name="update_clientprofile"),
    path("clients/list/", ClientListView.as_view(), name="client_list"),
    
    


]