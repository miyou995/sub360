from django.urls import path

from .views import (
    IndexView,
    set_language,
)

app_name = "core"


urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("set_language/<str:language>/", set_language, name="set_language"),
 
]
