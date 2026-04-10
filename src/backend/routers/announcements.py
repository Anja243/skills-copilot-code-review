"""
Announcement endpoints for school-wide communication.
"""

from datetime import date
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ..database import announcements_collection, teachers_collection

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"]
)


class AnnouncementPayload(BaseModel):
    """Request body for creating or updating announcements."""

    message: str = Field(..., min_length=1, max_length=500)
    start_date: Optional[date] = None
    expires_on: date


def _require_signed_in_teacher(teacher_username: Optional[str]) -> Dict[str, Any]:
    """Validate that a signed in teacher/admin user exists."""
    if not teacher_username:
        raise HTTPException(status_code=401, detail="Authentication required")

    teacher = teachers_collection.find_one({"_id": teacher_username})
    if not teacher:
        raise HTTPException(status_code=401, detail="Invalid teacher credentials")

    return teacher


def _validate_announcement_dates(payload: AnnouncementPayload) -> None:
    """Ensure dates are coherent for announcement visibility."""
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be blank")

    if payload.start_date and payload.start_date > payload.expires_on:
        raise HTTPException(
            status_code=400,
            detail="Start date must be on or before expiration date"
        )


def _serialize_announcement(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Convert MongoDB document into API response format."""
    return {
        "id": str(doc.get("_id")),
        "message": doc.get("message", ""),
        "start_date": doc.get("start_date"),
        "expires_on": doc.get("expires_on")
    }


@router.get("", response_model=List[Dict[str, Any]])
@router.get("/", response_model=List[Dict[str, Any]])
def get_active_announcements() -> List[Dict[str, Any]]:
    """Get currently active announcements visible to all users."""
    today = date.today().isoformat()

    query = {
        "expires_on": {"$gte": today},
        "$or": [
            {"start_date": None},
            {"start_date": {"$exists": False}},
            {"start_date": {"$lte": today}}
        ]
    }

    docs = announcements_collection.find(query).sort("expires_on", 1)
    return [_serialize_announcement(doc) for doc in docs]


@router.get("/all", response_model=List[Dict[str, Any]])
def get_all_announcements(teacher_username: Optional[str] = Query(None)) -> List[Dict[str, Any]]:
    """Get all announcements for management actions (requires auth)."""
    _require_signed_in_teacher(teacher_username)

    docs = announcements_collection.find({}).sort("expires_on", 1)
    return [_serialize_announcement(doc) for doc in docs]


@router.post("", response_model=Dict[str, Any])
@router.post("/", response_model=Dict[str, Any])
def create_announcement(
    payload: AnnouncementPayload,
    teacher_username: Optional[str] = Query(None)
) -> Dict[str, Any]:
    """Create a new announcement (requires auth)."""
    _require_signed_in_teacher(teacher_username)
    _validate_announcement_dates(payload)

    announcement_id = uuid4().hex
    doc = {
        "_id": announcement_id,
        "message": payload.message.strip(),
        "start_date": payload.start_date.isoformat() if payload.start_date else None,
        "expires_on": payload.expires_on.isoformat()
    }

    announcements_collection.insert_one(doc)
    return _serialize_announcement(doc)


@router.put("/{announcement_id}", response_model=Dict[str, Any])
def update_announcement(
    announcement_id: str,
    payload: AnnouncementPayload,
    teacher_username: Optional[str] = Query(None)
) -> Dict[str, Any]:
    """Update an existing announcement (requires auth)."""
    _require_signed_in_teacher(teacher_username)
    _validate_announcement_dates(payload)

    updated_doc = {
        "message": payload.message.strip(),
        "start_date": payload.start_date.isoformat() if payload.start_date else None,
        "expires_on": payload.expires_on.isoformat()
    }

    result = announcements_collection.update_one(
        {"_id": announcement_id},
        {"$set": updated_doc}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")

    stored = announcements_collection.find_one({"_id": announcement_id})
    if not stored:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return _serialize_announcement(stored)


@router.delete("/{announcement_id}", response_model=Dict[str, str])
def delete_announcement(
    announcement_id: str,
    teacher_username: Optional[str] = Query(None)
) -> Dict[str, str]:
    """Delete an announcement (requires auth)."""
    _require_signed_in_teacher(teacher_username)

    result = announcements_collection.delete_one({"_id": announcement_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")

    return {"message": "Announcement deleted"}
