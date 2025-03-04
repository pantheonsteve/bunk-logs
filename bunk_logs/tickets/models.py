from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from bunk_logs.bunks.models import Bunk
from bunk_logs.campers.models import Camper


class TicketType(models.Model):
    """Type of ticket (maintenance, store request, etc.)"""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = _("ticket type")
        verbose_name_plural = _("ticket types")

    def __str__(self):
        return self.name


class TicketStatus(models.TextChoices):
    PENDING = "PENDING", _("Pending")
    IN_PROGRESS = "IN_PROGRESS", _("In Progress")
    COMPLETED = "COMPLETED", _("Completed")
    CANCELLED = "CANCELLED", _("Cancelled")


class Ticket(models.Model):
    """Ticket for maintenance requests or store orders."""

    ticket_type = models.ForeignKey(
        TicketType,
        on_delete=models.CASCADE,
        related_name="tickets",
    )
    bunk = models.ForeignKey(Bunk, on_delete=models.CASCADE, related_name="tickets")
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="requested_tickets",
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=TicketStatus.choices,
        default=TicketStatus.PENDING,
    )

    # For tracking
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
    )
    resolution_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("ticket")
        verbose_name_plural = _("tickets")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.ticket_type.name} Ticket: {self.title}"


class StoreItem(models.Model):
    """Items available in the camper care store."""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100)
    is_available = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("store item")
        verbose_name_plural = _("store items")

    def __str__(self):
        return self.name


class StoreOrder(models.Model):
    """Order for items from the camper care store."""

    ticket = models.OneToOneField(
        Ticket,
        on_delete=models.CASCADE,
        related_name="store_order",
    )
    items = models.ManyToManyField(StoreItem, through="StoreOrderItem")
    camper = models.ForeignKey(
        Camper,
        on_delete=models.CASCADE,
        related_name="store_orders",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("store order")
        verbose_name_plural = _("store orders")

    def __str__(self):
        return f"Store Order #{self.id}"


class StoreOrderItem(models.Model):
    """Items included in a store order with quantity."""

    store_order = models.ForeignKey(StoreOrder, on_delete=models.CASCADE)
    store_item = models.ForeignKey(StoreItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = _("store order item")
        verbose_name_plural = _("store order items")

    def __str__(self):
        return f"{self.quantity} x {self.store_item.name}"
