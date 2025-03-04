# users/models.py
from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CharField
from django.db.models import EmailField
from django.db.models import ImageField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractUser):
    """
    Custom user model for Bunk Logs Project.
    """

    first_name = CharField(_("First Name"), blank=True, max_length=255)  # type: ignore[assignment]
    last_name = CharField(_("Last Name"), blank=True, max_length=255)  # type: ignore[assignment]
    email = EmailField(_("email"), unique=True)
    username = None  # type: ignore[assignment]

    # Added role functionality from accounts model
    class Role(models.TextChoices):
        COUNSELOR = "COUNSELOR", _("Counselor")
        CAMPER_CARE = "CAMPER_CARE", _("Camper Care Team")
        UNIT_HEAD = "UNIT_HEAD", _("Unit Head")
        ADMIN = "ADMIN", _("Administrator")

    role = CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.COUNSELOR,
    )
    phone_number = CharField(max_length=20, blank=True)
    profile_image = ImageField(upload_to="profile_images/", blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view."""
        return reverse("users:detail", kwargs={"pk": self.id})

    def is_counselor(self):
        return self.role == self.Role.COUNSELOR

    def is_camper_care(self):
        return self.role == self.Role.CAMPER_CARE

    def is_unit_head(self):
        return self.role == self.Role.UNIT_HEAD

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email
