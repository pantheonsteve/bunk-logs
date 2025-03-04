from datetime import datetime

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from bunk_logs.bunks.models import Bunk
from bunk_logs.bunks.models import Session


class Camper(models.Model):
    """Camper information."""

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    emergency_contact_name = models.CharField(max_length=255)
    emergency_contact_phone = models.CharField(max_length=20)
    medical_notes = models.TextField(blank=True)
    dietary_restrictions = models.TextField(blank=True)

    # Current status
    is_on_camp = models.BooleanField(default=True)
    status_note = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("camper")
        verbose_name_plural = _("campers")
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        today = datetime.now(tz=timezone.get_current_timezone()).date()
        return (
            today.year
            - self.date_of_birth.year
            - (
                (today.month, today.day)
                < (self.date_of_birth.month, self.date_of_birth.day)
            )
        )


class CamperBunkAssignment(models.Model):
    """Assignment of campers to bunks for a specific session."""

    camper = models.ForeignKey(
        Camper,
        on_delete=models.CASCADE,
        related_name="bunk_assignments",
    )
    bunk = models.ForeignKey(
        Bunk,
        on_delete=models.CASCADE,
        related_name="camper_assignments",
    )
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("camper bunk assignment")
        verbose_name_plural = _("camper bunk assignments")
        unique_together = ("camper", "session")

    def __str__(self):
        return f"{self.camper} in {self.bunk.name} ({self.session.name})"
