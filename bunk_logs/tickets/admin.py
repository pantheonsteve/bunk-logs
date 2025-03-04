from django.contrib import admin

from .models import StoreItem
from .models import StoreOrder
from .models import StoreOrderItem
from .models import Ticket
from .models import TicketType

# Basic registration
admin.site.register(TicketType)
admin.site.register(StoreItem)


# More customized registration
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "ticket_type",
        "bunk",
        "requested_by",
        "status",
        "created_at",
    )
    list_filter = ("status", "ticket_type", "bunk")
    search_fields = ("title", "description")
    date_hierarchy = "created_at"


@admin.register(StoreOrder)
class StoreOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "ticket", "camper")


@admin.register(StoreOrderItem)
class StoreOrderItemAdmin(admin.ModelAdmin):
    list_display = ("store_order", "store_item", "quantity")
