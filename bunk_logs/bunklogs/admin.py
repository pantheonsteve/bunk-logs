from django.contrib import admin

from .models import BunkLog


# Register your models here.
@admin.register(BunkLog)
class BunkLogAdmin(admin.ModelAdmin):
    list_display = (
        "camper",
        "date",
        "counselor",
        "social_score",
        "behavior_score",
        "participation_score",
    )
    search_fields = ("camper__name", "date", "counselor__username")
    autocomplete_fields = ["camper", "counselor"]
