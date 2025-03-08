# your_app/forms.py
from django import forms


class CabinCsvImportForm(forms.Form):
    csv_file = forms.FileField(
        label="CSV File",
        help_text="Please upload a CSV file with the required headers.",
    )
    dry_run = forms.BooleanField(
        required=False,
        label="Dry run",
        help_text="Validate the import without saving to database.",
    )

class UnitCsvImportForm(forms.Form):
    csv_file = forms.FileField(
        label='CSV File',
        help_text='Upload a CSV with columns: name, unit_head_email (or unit_head_username)'
    )
    dry_run = forms.BooleanField(
        required=False, 
        label='Dry run', 
        help_text='Validate without saving to database'
    )
    create_missing_users = forms.BooleanField(
        required=False,
        label='Create missing users',
        help_text='Create new unit head users if they don\'t exist (disabled)'
    )
