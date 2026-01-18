from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models import Material, Segment

router = APIRouter(prefix="/api/materials", tags=["materials"])


class MaterialResponse(BaseModel):
    """Material response schema."""

    id: int
    title: str
    source_type: str
    source_url: str | None
    audio_path: str
    duration: float
    thumbnail_path: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class SegmentResponse(BaseModel):
    """Segment response schema."""

    id: int
    text: str
    start_time: float
    end_time: float
    audio_path: str | None
    order: int

    class Config:
        from_attributes = True


class MaterialDetailResponse(MaterialResponse):
    """Material detail with segments."""

    segments: list[SegmentResponse]


@router.get("", response_model=list[MaterialResponse])
async def list_materials(db: AsyncSession = Depends(get_db)):
    """Get all materials."""
    result = await db.execute(
        select(Material).order_by(Material.created_at.desc())
    )
    materials = result.scalars().all()
    return materials


@router.get("/{material_id}", response_model=MaterialDetailResponse)
async def get_material(material_id: int, db: AsyncSession = Depends(get_db)):
    """Get material by ID with segments."""
    result = await db.execute(
        select(Material)
        .options(selectinload(Material.segments))
        .where(Material.id == material_id)
    )
    material = result.scalar_one_or_none()

    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    return material


@router.delete("/{material_id}")
async def delete_material(material_id: int, db: AsyncSession = Depends(get_db)):
    """Delete material and associated files."""
    result = await db.execute(
        select(Material).where(Material.id == material_id)
    )
    material = result.scalar_one_or_none()

    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    # TODO: Delete associated files from disk

    await db.delete(material)
    await db.commit()

    return {"message": "Material deleted successfully"}
