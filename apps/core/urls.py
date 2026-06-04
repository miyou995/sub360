from django.urls import path

from .views import (
    ConfigugrationView,
    IndexView,
    ManagePotentialHtmx,
    PotentialListView,
    StatisticsView,
    set_language,
)

app_name = "core"


urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("configuration", ConfigugrationView.as_view(), name="configuration"),
    path("set_language/<str:language>/", set_language, name="set_language"),
    path("statistics/", StatisticsView.as_view(), name="statistics"),
    # # tax---------------------------------------------------------------
    # # Potentiel---------------------------------------------------------------
    path("potentials/", PotentialListView.as_view(), name="list_potential"),
    path("potentials/create", ManagePotentialHtmx.as_view(), name="create_potential"),
    path(
        "potentials/update/<int:pk>",
        ManagePotentialHtmx.as_view(),
        name="update_potential",
    ),
]
