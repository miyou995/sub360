from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import CRUDUrlMixin, TimestampedModel

MIN_SCORE = 1
MAX_SCORE = 5


class RatingStatus(models.TextChoices):
    PENDING = "pending", _("En attente de modération")
    PUBLISHED = "published", _("Publié")
    REJECTED = "rejected", _("Rejeté")


class Rating(CRUDUrlMixin, TimestampedModel):
    """A client company's rating of a subcontractor.

    A client rates a subcontractor it has worked with (optionally tied to the
    tender the work was for). One rating per client company per subcontractor;
    it can be edited. Ratings are moderated by the back office before they are
    publicly visible.
    """

    subcontractor = models.ForeignKey(
        "subcontractors.Subcontractor",
        on_delete=models.CASCADE,
        related_name="ratings",
        verbose_name=_("Sous-traitant"),
    )
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="given_ratings",
        verbose_name=_("Entreprise"),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="ratings",
        verbose_name=_("Auteur"),
    )
    tender = models.ForeignKey(
        "tenders.Tender",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="ratings",
        verbose_name=_("Appel d'offres"),
    )
    score = models.PositiveSmallIntegerField(
        _("Note"),
        validators=[MinValueValidator(MIN_SCORE), MaxValueValidator(MAX_SCORE)],
        help_text=_("Note de %(min)d à %(max)d.")
        % {"min": MIN_SCORE, "max": MAX_SCORE},
    )
    comment = models.TextField(_("Commentaire"), blank=True)
    status = models.CharField(
        _("Statut"),
        max_length=10,
        choices=RatingStatus.choices,
        default=RatingStatus.PENDING,
    )

    class Meta:
        verbose_name = _("Évaluation")
        verbose_name_plural = _("Évaluations")
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("company", "subcontractor"),
                name="unique_rating_per_company_subcontractor",
            ),
            models.CheckConstraint(
                condition=models.Q(score__gte=MIN_SCORE, score__lte=MAX_SCORE),
                name="rating_score_between_1_and_5",
            ),
        ]

    def __str__(self):
        return f"{self.subcontractor} — {self.score}/5"
