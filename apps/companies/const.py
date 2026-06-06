# Constants for the companies app.

from django.db import models
from django.utils.translation import gettext_lazy as _


class CompanyType(models.TextChoices):
    CLIENT = "client", _("Client (entreprise donneuse d'ordre)")
    SUBCONTRACTOR = "subcontractor", _("Sous-traitant")
    BOTH = "both", _("Client et sous-traitant")


class SwissCanton(models.TextChoices):
    AG = "AG", "Aargau"
    AI = "AI", "Appenzell Innerrhoden"
    AR = "AR", "Appenzell Ausserrhoden"
    BE = "BE", "Bern"
    BL = "BL", "Basel-Landschaft"
    BS = "BS", "Basel-Stadt"
    FR = "FR", "Fribourg"
    GE = "GE", "Genève"
    GL = "GL", "Glarus"
    GR = "GR", "Graubünden"
    JU = "JU", "Jura"
    LU = "LU", "Luzern"
    NE = "NE", "Neuchâtel"
    NW = "NW", "Nidwalden"
    OW = "OW", "Obwalden"
    SG = "SG", "St. Gallen"
    SH = "SH", "Schaffhausen"
    SO = "SO", "Solothurn"
    SZ = "SZ", "Schwyz"
    TG = "TG", "Thurgau"
    TI = "TI", "Ticino"
    UR = "UR", "Uri"
    VD = "VD", "Vaud"
    VS = "VS", "Valais"
    ZG = "ZG", "Zug"
    ZH = "ZH", "Zürich"
