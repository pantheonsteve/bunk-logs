import csv
from pathlib import Path
from typing import Dict, List, Any, Union

from django.db import transaction

from bunk_logs.campers.models import Camper, CamperBunkAssignment
from bunk_logs.bunks.models import Bunk


class CamperImportError(ValueError):
    """Custom exception for camper import errors."""

    MISSING_FIRST_NAME = "First name is required"
    MISSING_LAST_NAME = "Last name is required"

def _validate_camper_names(first_name: str, last_name: str) -> None:
    """Validate camper names."""
    if not first_name:
        raise CamperImportError(CamperImportError.MISSING_FIRST_NAME)
    if not last_name:
        raise CamperImportError(CamperImportError.MISSING_LAST_NAME)
    
def import_campers_from_csv(file_path, *, dry_run=False):
    """Import campers from CSV file."""
    success_count = 0
    error_records = []
    file_path = Path(file_path)

    with file_path.open() as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            try:
                # Data validation
                if not row.get("first_name"):
                    msg = "First name is required"
                    raise ValueError(msg)
                if not row.get("last_name"):
                    msg = "Last name is required"
                    raise ValueError(msg)
                
                # Prepare data
                camper_data = {
                    "first_name": row["first_name"],
                    "last_name": row["last_name"],
                    "date_of_birth": row.get("date_of_birth") or None,
                    "emergency_contact_name": row.get("emergency_contact_name") or "",
                    "emergency_contact_phone": row.get("emergency_contact_phone") or "",
                    "camper_notes": row.get("camper_notes") or "",
                    "parent_notes": row.get("parent_notes") or "",
                }
                
                # Create camper
                camper = Camper(**camper_data)
                if not dry_run:
                    camper.save()
                
                success_count += 1
            except ValueError as e:
                error_records.append({"row": reader.line_num, "error": str(e)})

    return {
        "success_count": success_count,
        "error_count": len(error_records),
        "errors": error_records,
    }

class CamperBunkAssignmentError(ValueError):
    """Custom exception for camper bunk assignment import errors."""
    
    MISSING_CAMPER_NAME = "Camper first and last name are required"
    MISSING_BUNK_NAME = "Bunk name is required"

def _validate_camper_bunk_assignment_names(
    camper_first_name: str, camper_last_name: str, bunk_name: str
) -> None:
    """Validate camper bunk assignment names."""
    if not camper_first_name or not camper_last_name:
        raise CamperBunkAssignmentError(CamperBunkAssignmentError.MISSING_CAMPER_NAME)
    if not bunk_name:
        raise CamperBunkAssignmentError(CamperBunkAssignmentError.MISSING_BUNK_NAME)

def import_bunk_assignments_from_csv(
    file_path: Union[str, Path], *, dry_run: bool = False
) -> Dict[str, Any]:
    """
    Import camper bunk assignments from CSV file.
    
    Expected CSV format:
    camper_first_name,camper_last_name,cabin_name,session_name,start_date,end_date,is_active
    """
    success_count = 0
    error_records: List[Dict[str, Any]] = []
    
    file_path = Path(file_path)
    
    with file_path.open() as csv_file:
        reader = csv.DictReader(csv_file)
        
        for row in reader:
            # Process each row in its own transaction
            try:
                with transaction.atomic():
                    # Find the camper by first and last name
                    camper_first_name = row.get("camper_first_name", "").strip()
                    camper_last_name = row.get("camper_last_name", "").strip()
                    
                    if not camper_first_name or not camper_last_name:
                        raise ValueError("Camper first and last name are required")
                    
                    # Try to find existing camper
                    try:
                        camper = Camper.objects.get(
                            first_name__iexact=camper_first_name,
                            last_name__iexact=camper_last_name
                        )
                    except Camper.DoesNotExist:
                        # Create a new camper
                        camper = Camper(
                            first_name=camper_first_name,
                            last_name=camper_last_name,
                            date_of_birth=None,  # Set date_of_birth to None to avoid validation error
                            emergency_contact_name="",
                            emergency_contact_phone="",
                            camper_notes="",
                            parent_notes="",
                        )
                        if not dry_run:
                            camper.save()
                    except Camper.MultipleObjectsReturned:
                        raise ValueError(f"Multiple campers found with name {camper_first_name} {camper_last_name}")
                    
                    # Find the cabin and session
                    cabin_name = row.get("cabin_name", "").strip()
                    session_name = row.get("session_name", "").strip()
                    
                    if not cabin_name or not session_name:
                        raise ValueError("Both cabin name and session name are required")
                    
                    from bunk_logs.bunks.models import Cabin, Session
                    
                    try:
                        cabin = Cabin.objects.get(name__iexact=cabin_name)
                    except Cabin.DoesNotExist:
                        raise ValueError(f"Cabin '{cabin_name}' not found")
                    
                    try:
                        session = Session.objects.get(name__iexact=session_name)
                    except Session.DoesNotExist:
                        raise ValueError(f"Session '{session_name}' not found")
                    
                    # Find the bunk using cabin and session
                    try:
                        bunk = Bunk.objects.get(cabin=cabin, session=session)
                    except Bunk.DoesNotExist:
                        raise ValueError(f"Bunk with cabin '{cabin_name}' and session '{session_name}' not found")
                    except Bunk.MultipleObjectsReturned:
                        raise ValueError(f"Multiple bunks found with cabin '{cabin_name}' and session '{session_name}'")
                    
                    # Parse dates if provided
                    start_date = row.get("start_date", "").strip() or None
                    end_date = row.get("end_date", "").strip() or None
                    
                    # Parse is_active
                    is_active_str = row.get("is_active", "").strip().lower()
                    is_active = True  # Default
                    if is_active_str in ("false", "0", "no", "n"):
                        is_active = False
                    
                    # In dry run mode, we validate but don't save
                    if not dry_run:
                        # Create assignment
                        assignment, created = CamperBunkAssignment.objects.update_or_create(
                            camper=camper,
                            bunk=bunk,
                            defaults={
                                "start_date": start_date,
                                "end_date": end_date,
                                "is_active": is_active,
                            }
                        )
                    
                    success_count += 1
            except Exception as e:
                error_records.append({
                    "row": row,
                    "error": str(e),
                })
    
    return {
        "success_count": success_count,
        "error_count": len(error_records),
        "errors": error_records,
    }



