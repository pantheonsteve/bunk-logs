import csv
from pathlib import Path
from typing import Any

from bunk_logs.bunks.models import Cabin, Unit  # Adjust based on your actual model

class UnitImportError(ValueError):
    """Custom exception for unit import errors."""

    MISSING_NAME = "Unit name is required"

def _validate_unit_name(name: str) -> None:
    """Validate unit name."""
    if not name:
        raise UnitImportError(UnitImportError.MISSING_NAME)
    
def import_units_from_csv(file_path, *, dry_run=False):
    """Import units from CSV file."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    success_count = 0
    error_records = []
    file_path = Path(file_path)
    
    with file_path.open() as csv_file:
        reader = csv.DictReader(csv_file)
        
        for row in reader:
            try:
                # Data validation
                if not row.get("name"):
                    msg = "Unit name is required"
                    raise ValueError(msg)
                
                # Prepare data
                unit_data = {
                    "name": row["name"],
                }
                
                # Look up unit head by email or username if provided
                unit_head_identifier = row.get("unit_head_email") or row.get("unit_head_username")
                unit_head = None
                
                if unit_head_identifier:
                    # Try email first
                    if "@" in unit_head_identifier:
                        unit_head = User.objects.filter(
                            email=unit_head_identifier, 
                            role="UNIT_HEAD"
                        ).first()
                    else:
                        # Then try username
                        unit_head = User.objects.filter(
                            username=unit_head_identifier, 
                            role="UNIT_HEAD"
                        ).first()
                    
                    if not unit_head:
                        notes = f"Unit head with identifier {unit_head_identifier} not found"
                        unit_data["unit_head"] = None  # Will be None anyway, but explicit
                    else:
                        unit_data["unit_head"] = unit_head
                
                # In dry run mode, we validate but don't save
                if not dry_run:
                    # Create or update unit
                    unit, created = Unit.objects.update_or_create(
                        name=row["name"],
                        defaults=unit_data,
                    )
                
                success_count += 1
            except (ValueError, TypeError, KeyError) as e:
                error_records.append({
                    "row": row,
                    "error": str(e),
                })
    
    return {
        "success_count": success_count,
        "error_count": len(error_records),
        "errors": error_records,
    }

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
