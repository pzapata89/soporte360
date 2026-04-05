from sqlalchemy.orm import Session
from sqlalchemy import func, extract, case
from datetime import datetime, timedelta
from typing import List, Optional
from app.models import Ticket, TicketStatus, TicketComment, TicketHistory, User, UserRole, Category
from app.schemas import GeneralReport, CategoryReportItem, TechnicianReportItem


def get_general_report(db: Session) -> GeneralReport:
    """Generate general statistics report"""
    
    # Total tickets
    total = db.query(Ticket).count()
    
    # Tickets by status
    open_count = db.query(Ticket).filter(Ticket.status == TicketStatus.OPEN).count()
    closed_count = db.query(Ticket).filter(Ticket.status == TicketStatus.CLOSED).count()
    in_progress_count = db.query(Ticket).filter(Ticket.status == TicketStatus.IN_PROGRESS).count()
    on_hold_count = db.query(Ticket).filter(Ticket.status == TicketStatus.ON_HOLD).count()
    
    # Average resolution time for closed tickets
    avg_resolution = db.query(
        func.avg(
            extract('epoch', Ticket.closed_at - Ticket.created_at) / 3600
        )
    ).filter(
        Ticket.status == TicketStatus.CLOSED,
        Ticket.closed_at.isnot(None)
    ).scalar()
    
    return GeneralReport(
        total_tickets=total,
        open_tickets=open_count,
        closed_tickets=closed_count,
        in_progress_tickets=in_progress_count,
        on_hold_tickets=on_hold_count,
        avg_resolution_time_hours=round(avg_resolution, 2) if avg_resolution else None
    )


def get_category_report(db: Session) -> List[CategoryReportItem]:
    """Generate report of tickets by category"""
    
    results = db.query(
        Category.id,
        Category.name,
        func.count(Ticket.id).label('total'),
        func.sum(case((Ticket.status != TicketStatus.CLOSED, 1), else_=0)).label('open'),
        func.sum(case((Ticket.status == TicketStatus.CLOSED, 1), else_=0)).label('closed')
    ).outerjoin(
        Ticket, Category.id == Ticket.category_id
    ).group_by(
        Category.id, Category.name
    ).all()
    
    return [
        CategoryReportItem(
            category_id=row.id,
            category_name=row.name,
            total_tickets=row.total or 0,
            open_tickets=row.open or 0,
            closed_tickets=row.closed or 0
        )
        for row in results
    ]


def get_technician_report(db: Session) -> List[TechnicianReportItem]:
    """Generate report of tickets by technician"""
    
    results = db.query(
        User.id,
        User.full_name,
        func.count(Ticket.id).label('total'),
        func.sum(case((Ticket.status == TicketStatus.OPEN, 1), else_=0)).label('open'),
        func.sum(case((Ticket.status == TicketStatus.CLOSED, 1), else_=0)).label('closed'),
        func.sum(case((Ticket.status == TicketStatus.IN_PROGRESS, 1), else_=0)).label('in_progress')
    ).outerjoin(
        Ticket, User.id == Ticket.assigned_to
    ).filter(
        User.role == UserRole.TECNICO
    ).group_by(
        User.id, User.full_name
    ).all()
    
    return [
        TechnicianReportItem(
            user_id=row.id,
            full_name=row.full_name,
            total_assigned=row.total or 0,
            open_tickets=row.open or 0,
            closed_tickets=row.closed or 0,
            in_progress_tickets=row.in_progress or 0
        )
        for row in results
    ]
