from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User
from app.schemas import GeneralReport, CategoryReportItem, TechnicianReportItem
from app.services import report_service
from app.core.auth import require_supervisor

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/general", response_model=GeneralReport)
def get_general_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_supervisor)
):
    """Get general ticket statistics report"""
    return report_service.get_general_report(db)


@router.get("/by-category", response_model=List[CategoryReportItem])
def get_category_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_supervisor)
):
    """Get ticket statistics grouped by category"""
    return report_service.get_category_report(db)


@router.get("/by-technician", response_model=List[TechnicianReportItem])
def get_technician_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_supervisor)
):
    """Get ticket statistics grouped by technician"""
    return report_service.get_technician_report(db)
