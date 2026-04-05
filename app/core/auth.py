from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserRole
from app.core.security import decode_token

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
        )
    
    return user


def require_role(allowed_roles: list[UserRole]):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        # Handle case sensitivity - convert both to lowercase for comparison
        if hasattr(current_user.role, 'value'):
            # It's an enum
            user_role_value = current_user.role.value
        else:
            # It's already a string (maybe from DB)
            user_role_value = str(current_user.role)
        
        user_role_str = user_role_value.lower()
        
        is_authorized = False
        for allowed_role in allowed_roles:
            allowed_role_str = allowed_role.value.lower()
            if user_role_str == allowed_role_str:
                is_authorized = True
                break
        
        if not is_authorized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {user_role_value} not authorized for this action",
            )
        return current_user
    return role_checker


# Role dependencies
require_admin = require_role([UserRole.ADMIN])
require_supervisor = require_role([UserRole.ADMIN, UserRole.SUPERVISOR])
require_tecnico = require_role([UserRole.ADMIN, UserRole.SUPERVISOR, UserRole.TECNICO])
require_any_user = require_role([UserRole.ADMIN, UserRole.SUPERVISOR, UserRole.TECNICO, UserRole.USUARIO])
