from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.models import UserRole, TicketStatus, TicketPriority, HistoryAction


# ============ USER SCHEMAS ============

class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)
    role: UserRole
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=255)


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserBulkCreate(BaseModel):
    users: List[UserCreate]


# ============ CATEGORY SCHEMAS ============

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    is_active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ TICKET SCHEMAS ============

class TicketBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    priority: TicketPriority = TicketPriority.MEDIUM
    category_id: int


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    priority: Optional[TicketPriority] = None
    category_id: Optional[int] = None


class TicketStatusUpdate(BaseModel):
    status: TicketStatus


class TicketAssign(BaseModel):
    assigned_to: Optional[int] = None


class TicketResponse(BaseModel):
    id: int
    ticket_code: str
    title: str
    description: str
    status: TicketStatus
    priority: TicketPriority
    category_id: int
    created_by: int
    assigned_to: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    closed_at: Optional[datetime]
    category: CategoryResponse
    creator: UserResponse
    assignee: Optional[UserResponse]

    class Config:
        from_attributes = True


class TicketListResponse(BaseModel):
    id: int
    ticket_code: str
    title: str
    status: TicketStatus
    priority: TicketPriority
    category_id: int
    created_by: int
    assigned_to: Optional[int]
    assigned_to_name: Optional[str] = None
    creator_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]
    closed_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============ TICKET COMMENT SCHEMAS ============

class TicketCommentBase(BaseModel):
    comment: str = Field(..., min_length=1)


class TicketCommentCreate(TicketCommentBase):
    pass


class TicketCommentResponse(TicketCommentBase):
    id: int
    ticket_id: int
    user_id: int
    created_at: datetime
    user: UserResponse

    class Config:
        from_attributes = True


# ============ TICKET HISTORY SCHEMAS ============

class TicketHistoryBase(BaseModel):
    action: HistoryAction
    from_status: Optional[str] = None
    to_status: Optional[str] = None


class TicketHistoryResponse(TicketHistoryBase):
    id: int
    ticket_id: int
    user_id: int
    timestamp: datetime
    user: UserResponse

    class Config:
        from_attributes = True


# ============ AUTH SCHEMAS ============

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    email: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ============ REPORT SCHEMAS ============

class GeneralReport(BaseModel):
    total_tickets: int
    open_tickets: int
    closed_tickets: int
    in_progress_tickets: int
    on_hold_tickets: int
    avg_resolution_time_hours: Optional[float]


class CategoryReportItem(BaseModel):
    category_id: int
    category_name: str
    total_tickets: int
    open_tickets: int
    closed_tickets: int


class TechnicianReportItem(BaseModel):
    user_id: int
    full_name: str
    total_assigned: int
    open_tickets: int
    closed_tickets: int
    in_progress_tickets: int
