from django.contrib import admin

from .models import Camper
from .models import CamperBunkAssignment


@admin.register(Camper)
class CamperAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "age")  # Adjust fields as needed
    list_filter = ("last_name", "first_name")
    search_fields = ("first_name", "last_name", "age")


@admin.register(CamperBunkAssignment)
class CamperBunkAssignmentAdmin(admin.ModelAdmin):
    list_display = ("camper", "bunk", "session", "is_active")  # Adjust fields as needed
    list_filter = ("session", "bunk")
    search_fields = ("camper", "bunk", "session")
