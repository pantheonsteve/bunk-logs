import csv
from pathlib import Path
from typing import Any

from bunk_logs.bunks.models import Cabin  # Adjust based on your actual model


class CabinImportError(ValueError):
    """Custom exception for cabin import errors."""

    MISSING_NAME = "Cabin name is required"


def _validate_cabin_name(name: str) -> None:
    """Validate cabin name."""
    if not name:
        raise CabinImportError(CabinImportError.MISSING_NAME)


def import_cabins_from_csv(
    file_path: str | Path,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Import cabins from CSV file.

    Args:
        file_path: Path to the CSV file
        dry_run: If True, validate the data without saving to database

    Returns:
        Dictionary with import results
    """
    success_count = 0
    error_records: list[dict[str, Any]] = []

    file_path = Path(file_path)

    with file_path.open() as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            try:
                # Data validation
                name = row.get("name", "")
                _validate_cabin_name(name)

                # Transform data if needed
                capacity = int(row.get("capacity", 0))

                # In dry run mode, we validate but don't save
                if not dry_run:
                    # Create or update cabin
                    cabin, created = Cabin.objects.update_or_create(
                        name=row["name"],
                        defaults={
                            "capacity": capacity,
                            "location": row.get("location", ""),
                            "notes": row.get("notes", ""),  # Matches your model
                            # Add other fields as needed
                        },
                    )

                success_count += 1
            except (ValueError, TypeError, KeyError) as e:
                error_records.append(
                    {
                        "row": row,
                        "error": str(e),
                    },
                )

    return {
        "success_count": success_count,
        "error_count": len(error_records),
        "errors": error_records,
    }
