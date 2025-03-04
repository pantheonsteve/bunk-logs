from django.conf import settings
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from bunk_logs.campers.models import Camper


class BunkLog(models.Model):
    """Daily report for each camper."""

    camper = models.ForeignKey(
        Camper,
        on_delete=models.CASCADE,
        related_name="bunk_logs",
    )
    date = models.DateField()
    counselor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="submitted_logs",
    )

    # Scores (1-5 scale)
    social_score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
    )
    behavior_score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
    )
    participation_score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
    )

    # Status flags
    camper_not_on_camp = models.BooleanField(default=False)
    request_camper_care_help = models.BooleanField(default=False)
    request_unit_head_help = models.BooleanField(default=False)

    # Details
    description = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("bunk log")
        verbose_name_plural = _("bunk logs")
        unique_together = ("camper", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"Log for {self.camper} on {self.date}"
