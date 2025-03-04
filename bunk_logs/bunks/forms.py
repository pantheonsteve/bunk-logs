# your_app/forms.py
from django import forms


class CsvImportForm(forms.Form):
    csv_file = forms.FileField(
        label="CSV File",
        help_text="Please upload a CSV file with the required headers.",
    )
    dry_run = forms.BooleanField(
        required=False,
        label="Dry run",
        help_text="Validate the import without saving to database.",
    )
