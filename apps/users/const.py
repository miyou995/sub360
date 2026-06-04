# Constants for the users app.

from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRole(models.TextChoices):
    CLIENT = "client", _("Client")
    SUBCONTRACTOR = "subcontractor", _("Sous-traitant")
    ADMIN = "admin", _("Back office")


class Language(models.TextChoices):
    DE = "de", _("Deutsch")
    FR = "fr", _("Français")
    IT = "it", _("Italiano")
    EN = "en", _("English")
