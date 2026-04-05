from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import User, UserRole, TicketStatus, TicketPriority
from app.schemas import (
    CategoryCreate, CategoryResponse,
    TicketCreate, TicketUpdate, TicketResponse, TicketListResponse,
    TicketCommentCreate, TicketCommentResponse,
    TicketHistoryResponse, TicketStatusUpdate, TicketAssign
)
from app.services import ticket_service, category_service
from app.core.auth import require_admin, require_supervisor, require_tecnico, require_any_user, get_current_user

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_user)
):
    # Validate category exists
    category = category_service.get_category_by_id(db, ticket_data.category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Create ticket
    ticket = ticket_service.create_ticket(db, ticket_data, current_user.id)
    
    # Create history entry for creation
    ticket_service.create_history_entry(
        db=db,
        ticket_id=ticket.id,
        user_id=current_user.id,
        action="CREATION",
        to_status=ticket.status
    )
    
    # Create history entry for auto-assignment if applicable
    if ticket.assigned_to:
        ticket_service.create_history_entry(
            db=db,
            ticket_id=ticket.id,
            user_id=current_user.id,
            action="ASSIGNMENT"
        )
    
    return ticket


@router.get("", response_model=List[TicketListResponse])
def get_tickets(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category_id: Optional[str] = None,
    assigned_to: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_user)
):
    # Convert string parameters to proper types or None
    status_enum = None
    if status and status.strip():
        try:
            status_enum = TicketStatus(status.lower())
        except ValueError:
            pass
    
    priority_enum = None
    if priority and priority.strip():
        try:
            priority_enum = TicketPriority(priority.lower())
        except ValueError:
            pass
    
    category_id_int = None
    if category_id and category_id.strip():
        try:
            category_id_int = int(category_id)
        except ValueError:
            pass
    
    assigned_to_int = None
    if assigned_to and assigned_to.strip():
        try:
            assigned_to_int = int(assigned_to)
        except ValueError:
            pass
    
    return ticket_service.get_tickets(
        db, current_user, skip, limit, status_enum, priority_enum, category_id_int, assigned_to_int
    )


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_user)
):
    ticket = ticket_service.get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Check permissions based on role
    if hasattr(current_user.role, 'value'):
        # It's an enum
        user_role_value = current_user.role.value
    else:
        # It's already a string (maybe from DB)
        user_role_value = str(current_user.role)
    
    user_role_str = user_role_value.lower()
    
    # Admin and Supervisor can see all tickets
    if user_role_str in [UserRole.ADMIN.value, UserRole.SUPERVISOR.value]:
        pass  # No restrictions
    elif user_role_str == UserRole.USUARIO.value:
        # Users can only see their own tickets
        if ticket.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this ticket"
            )
    elif user_role_str == UserRole.TECNICO.value:
        # Technicians can see tickets assigned to them or created by them
        if ticket.assigned_to != current_user.id and ticket.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this ticket"
            )
    
    return ticket


@router.put("/{ticket_id}/status", response_model=TicketResponse)
def update_ticket_status(
    ticket_id: int,
    status_update: TicketStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_user)
):
    ticket = ticket_service.get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    # Check permissions
    if hasattr(current_user.role, 'value'):
        user_role_value = current_user.role.value
    else:
        user_role_value = str(current_user.role)

    user_role_str = user_role_value.lower()

    # Usuario role can only close or reopen their own tickets
    if user_role_str == UserRole.USUARIO.value:
        if ticket.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this ticket"
            )
        allowed_statuses = {TicketStatus.CLOSED, TicketStatus.OPEN}
        if status_update.status not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Users can only close or reopen tickets"
            )

    # Admin and Supervisor can update all tickets
    if user_role_str in [UserRole.ADMIN.value, UserRole.SUPERVISOR.value]:
        pass  # No restrictions
    elif user_role_str == UserRole.TECNICO.value:
        # Technicians can update tickets assigned to them or created by them
        if ticket.assigned_to != current_user.id and ticket.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this ticket"
            )
    
    old_status = ticket.status
    updated_ticket = ticket_service.update_ticket_status(
        db, ticket, status_update.status, current_user.id
    )
    
    # Create history entry
    ticket_service.create_history_entry(
        db=db,
        ticket_id=ticket.id,
        user_id=current_user.id,
        action="STATUS_CHANGE",
        from_status=old_status,
        to_status=status_update.status
    )
    
    return updated_ticket


@router.put("/{ticket_id}/assign", response_model=TicketResponse)
def assign_ticket(
    ticket_id: int,
    assign_data: TicketAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_supervisor)
):
    ticket = ticket_service.get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    old_assigned = str(ticket.assigned_to) if ticket.assigned_to else None
    new_assigned = str(assign_data.assigned_to) if assign_data.assigned_to else None
    
    updated_ticket = ticket_service.assign_ticket(db, ticket, assign_data.assigned_to)
    
    # Create history entry
    ticket_service.create_history_entry(
        db=db,
        ticket_id=ticket.id,
        user_id=current_user.id,
        action="ASSIGNMENT"
    )
    
    return updated_ticket


@router.post("/{ticket_id}/comments", response_model=TicketCommentResponse)
def create_comment(
    ticket_id: int,
    comment_data: TicketCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_user)
):
    ticket = ticket_service.get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Check permissions
    if hasattr(current_user.role, 'value'):
        # It's an enum
        user_role_value = current_user.role.value
    else:
        # It's already a string (maybe from DB)
        user_role_value = str(current_user.role)
    
    user_role_str = user_role_value.lower()
    
    # Admin and Supervisor can comment on all tickets
    if user_role_str in [UserRole.ADMIN.value, UserRole.SUPERVISOR.value]:
        pass  # No restrictions
    elif user_role_str == UserRole.USUARIO.value:
        # Users can only comment on their own tickets
        if ticket.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to comment on this ticket"
            )
    elif user_role_str == UserRole.TECNICO.value:
        # Technicians can comment on tickets assigned to them or created by them
        if ticket.assigned_to != current_user.id and ticket.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to comment on this ticket"
            )
    
    comment = ticket_service.create_comment(db, ticket_id, current_user.id, comment_data)
    
    # Create history entry
    ticket_service.create_history_entry(
        db=db,
        ticket_id=ticket_id,
        user_id=current_user.id,
        action="COMMENT"
    )
    
    return comment


@router.get("/{ticket_id}/comments", response_model=List[TicketCommentResponse])
def get_comments(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_user)
):
    ticket = ticket_service.get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    if hasattr(current_user.role, 'value'):
        user_role_value = current_user.role.value
    else:
        user_role_value = str(current_user.role)

    if user_role_value.lower() == UserRole.USUARIO.value:
        if ticket.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view comments on this ticket"
            )

    return ticket_service.get_comments_by_ticket(db, ticket_id)


@router.get("/{ticket_id}/history", response_model=List[TicketHistoryResponse])
def get_history(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_user)
):
    ticket = ticket_service.get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Check permissions
    if hasattr(current_user.role, 'value'):
        # It's an enum
        user_role_value = current_user.role.value
    else:
        # It's already a string (maybe from DB)
        user_role_value = str(current_user.role)
    
    user_role_str = user_role_value.lower()
    
    # Admin and Supervisor can see all ticket history
    if user_role_str in [UserRole.ADMIN.value, UserRole.SUPERVISOR.value]:
        pass  # No restrictions
    elif user_role_str == UserRole.USUARIO.value:
        # Users can only see their own ticket history
        if ticket.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this ticket history"
            )
    elif user_role_str == UserRole.TECNICO.value:
        # Technicians can see history of tickets assigned to them or created by them
        if ticket.assigned_to != current_user.id and ticket.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this ticket history"
            )
    
    return ticket_service.get_history_by_ticket(db, ticket_id)
