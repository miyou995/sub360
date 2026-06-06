# Constants for the users app.

from django.db import models
from django.utils.translation import gettext_lazy as _


class WorkerCount(models.TextChoices):
    R1_5 = "1-5", _("1 à 5")
    R6_10 = "6-10", _("6 à 10")
    R11_25 = "11-25", _("11 à 25")
    R26_50 = "26-50", _("26 à 50")
    R51_100 = "51-100", _("51 à 100")
    R100_PLUS = "100+", _("Plus de 100")


class CompanyAge(models.TextChoices):
    UNDER_3 = "under_3", _("Moins de 3 ans")
    BETWEEN_3_10 = "3_10", _("3 à 10 ans")
    OVER_10 = "over_10", _("Plus de 10 ans")
