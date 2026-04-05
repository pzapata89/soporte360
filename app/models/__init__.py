import enum
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum, func, text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from app.database import Base


# ENUMS
class UserRole(enum.Enum):
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    TECNICO = "tecnico"
    USUARIO = "usuario"


class TicketStatus(enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    CLOSED = "closed"


class TicketPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class HistoryAction(enum.Enum):
    CREATION = "creation"
    STATUS_CHANGE = "status_change"
    ASSIGNMENT = "assignment"
    COMMENT = "comment"


# MODELOS
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column("password", String(255), nullable=False)
    full_name = Column("nombre", String(255), nullable=False)
    role = Column("rol", PG_ENUM(UserRole, name="user_role", create_type=False), nullable=False)
    is_active = Column("activo", Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relaciones
    created_tickets = relationship("Ticket", foreign_keys="Ticket.created_by", back_populates="creator")
    assigned_tickets = relationship("Ticket", foreign_keys="Ticket.assigned_to", back_populates="assignee")
    comments = relationship("TicketComment", back_populates="user")
    history_entries = relationship("TicketHistory", back_populates="user")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column("nombre", String(100), unique=True, nullable=False)
    is_active = Column("activa", Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relaciones
    tickets = relationship("Ticket", back_populates="category")


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_code = Column(String(20), unique=True, nullable=False, index=True)
    title = Column("titulo", String(255), nullable=False)
    description = Column("descripcion", Text, nullable=False)
    status = Column("estado", PG_ENUM(TicketStatus, name="ticket_status", create_type=False), default=TicketStatus.OPEN, nullable=False)
    priority = Column("prioridad", PG_ENUM(TicketPriority, name="ticket_priority", create_type=False), default=TicketPriority.MEDIUM, nullable=False)
    category_id = Column("categoria_id", Integer, ForeignKey("categories.id"), nullable=False)
    created_by = Column("creado_por", Integer, ForeignKey("users.id"), nullable=False)
    assigned_to = Column("asignado_a", Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True))
    closed_at = Column(DateTime(timezone=True))

    # Relaciones
    category = relationship("Category", back_populates="tickets")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_tickets")
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_tickets")
    comments = relationship("TicketComment", back_populates="ticket")
    history_entries = relationship("TicketHistory", back_populates="ticket")


class TicketComment(Base):
    __tablename__ = "ticket_comments"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comment = Column("comentario", Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relaciones
    ticket = relationship("Ticket", back_populates="comments")
    user = relationship("User", back_populates="comments")


class TicketHistory(Base):
    __tablename__ = "ticket_history"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column("accion", PG_ENUM(HistoryAction, name="history_action", create_type=False), nullable=False)
    from_status = Column(PG_ENUM(TicketStatus, name="ticket_status", create_type=False))
    to_status = Column(PG_ENUM(TicketStatus, name="ticket_status", create_type=False))
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relaciones
    ticket = relationship("Ticket", back_populates="history_entries")
    user = relationship("User", back_populates="history_entries")
