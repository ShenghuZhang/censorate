from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.template import Template
from app.schemas.template import TemplateResponse, TemplateCreate

router = APIRouter()


@router.get("/", response_model=List[TemplateResponse])
def list_templates(db: Session = Depends(get_db)):
    """List all active templates."""
    return db.query(Template).filter(Template.is_active.is_(True)).all()


@router.get("/{template_id}", response_model=TemplateResponse)
def get_template(template_id: str, db: Session = Depends(get_db)):
    """Get a specific template by ID."""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.post("/", response_model=TemplateResponse, status_code=201)
def create_template(data: TemplateCreate, db: Session = Depends(get_db)):
    """Create a new template."""
    existing = db.query(Template).filter(Template.slug == data.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Template with this slug already exists")
    template = Template(**data.model_dump())
    db.add(template)
    db.commit()
    db.refresh(template)
    return template
