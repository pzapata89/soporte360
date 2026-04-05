from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_, or_
from typing import Optional, List
from datetime import datetime
from app.models import (
    Ticket, TicketStatus, TicketPriority, TicketComment, 
    TicketHistory, HistoryAction, User, UserRole
)
from app.schemas import TicketCreate, TicketUpdate, TicketCommentCreate, TicketStatusUpdate
from app.services import user_service


def get_ticket_by_id(db: Session, ticket_id: int) -> Optional[Ticket]:
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()


def get_ticket_by_code(db: Session, ticket_code: str) -> Optional[Ticket]:
    return db.query(Ticket).filter(Ticket.ticket_code == ticket_code).first()


def get_tickets(
    db: Session,
    user: User,
    skip: int = 0,
    limit: int = 100,
    status: Optional[TicketStatus] = None,
    priority: Optional[TicketPriority] = None,
    category_id: Optional[int] = None,
    assigned_to: Optional[int] = None
) -> List[Ticket]:
    query = db.query(Ticket).outerjoin(User, Ticket.assigned_to == User.id)
    
    # Filter by role
    if hasattr(user.role, 'value'):
        user_role_value = user.role.value
    else:
        user_role_value = str(user.role)
    user_role_str = user_role_value.lower()
    
    if user_role_str == UserRole.USUARIO.value:
        query = query.filter(Ticket.created_by == user.id)
    elif user_role_str == UserRole.TECNICO.value:
        query = query.filter(
            or_(
                Ticket.assigned_to == user.id,
                Ticket.created_by == user.id
            )
        )
    # ADMIN y SUPERVISOR ven todos
    
    # Apply filters
    if status:
        query = query.filter(Ticket.status == status)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if category_id:
        query = query.filter(Ticket.category_id == category_id)
    if assigned_to:
        query = query.filter(Ticket.assigned_to == assigned_to)
    
    tickets = query.order_by(Ticket.created_at.desc()).offset(skip).limit(limit).all()
    
    # Add assigned_to_name and creator_name to each ticket
    for ticket in tickets:
        # Get assignee name
        if ticket.assigned_to:
            assignee = db.query(User).filter(User.id == ticket.assigned_to).first()
            ticket.assigned_to_name = assignee.full_name if assignee else None
        else:
            ticket.assigned_to_name = None
            
        # Get creator name
        creator = db.query(User).filter(User.id == ticket.created_by).first()
        ticket.creator_name = creator.full_name if creator else None
    
    return tickets


def count_open_tickets_for_technician(db: Session, technician_id: int) -> int:
    """Count tickets that are considered 'open' for workload calculation"""
    return db.query(Ticket).filter(
        Ticket.assigned_to == technician_id,
        Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS, TicketStatus.ON_HOLD])
    ).count()


def find_best_technician(db: Session) -> Optional[User]:
    """Find technician with lowest workload"""
    technicians = user_service.get_active_technicians(db)
    if not technicians:
        return None
    
    best_technician = None
    lowest_load = float('inf')
    
    for tech in technicians:
        load = count_open_tickets_for_technician(db, tech.id)
        if load < lowest_load:
            lowest_load = load
            best_technician = tech
    
    return best_technician


def create_ticket(db: Session, ticket_data: TicketCreate, created_by: int) -> Ticket:
    # Find best technician for auto-assignment
    best_tech = find_best_technician(db)
    
    # Generate ticket code
    ticket_count = db.query(func.count(Ticket.id)).scalar() + 1
    ticket_code = f"TK-{datetime.now().strftime('%Y%m')}-{ticket_count:04d}"
    
    db_ticket = Ticket(
        ticket_code=ticket_code,
        title=ticket_data.title,
        description=ticket_data.description,
        priority=ticket_data.priority,
        category_id=ticket_data.category_id,
        created_by=created_by,
        assigned_to=best_tech.id if best_tech else None,
        status=TicketStatus.OPEN
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    
    return db_ticket


def update_ticket(db: Session, ticket: Ticket, ticket_data: TicketUpdate) -> Ticket:
    update_data = ticket_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ticket, field, value)
    db.commit()
    db.refresh(ticket)
    return ticket


def update_ticket_status(db: Session, ticket: Ticket, new_status: TicketStatus, user_id: int) -> Ticket:
    old_status = ticket.status
    ticket.status = new_status
    
    # Si se cierra, setear closed_at
    if new_status == TicketStatus.CLOSED:
        ticket.closed_at = datetime.utcnow()
    else:
        ticket.closed_at = None
    
    db.commit()
    db.refresh(ticket)
    return ticket


def assign_ticket(db: Session, ticket: Ticket, assigned_to: Optional[int]) -> Ticket:
    ticket.assigned_to = assigned_to
    db.commit()
    db.refresh(ticket)
    return ticket


def create_comment(db: Session, ticket_id: int, user_id: int, comment_data: TicketCommentCreate) -> TicketComment:
    db_comment = TicketComment(
        ticket_id=ticket_id,
        user_id=user_id,
        comment=comment_data.comment
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def get_comments_by_ticket(db: Session, ticket_id: int) -> List[TicketComment]:
    return db.query(TicketComment).filter(
        TicketComment.ticket_id == ticket_id
    ).order_by(TicketComment.created_at.asc()).all()


def create_history_entry(
    db: Session,
    ticket_id: int,
    user_id: int,
    action: str,
    from_status: Optional[TicketStatus] = None,
    to_status: Optional[TicketStatus] = None
) -> TicketHistory:
    # Convert string action to HistoryAction enum
    action_enum = HistoryAction(action.lower())
    
    db_history = TicketHistory(
        ticket_id=ticket_id,
        user_id=user_id,
        action=action_enum,
        from_status=from_status,
        to_status=to_status
    )
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history


def get_history_by_ticket(db: Session, ticket_id: int) -> List[TicketHistory]:
    return db.query(TicketHistory).filter(
        TicketHistory.ticket_id == ticket_id
    ).order_by(TicketHistory.timestamp.desc()).all()
