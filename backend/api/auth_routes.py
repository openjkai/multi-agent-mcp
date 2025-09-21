"""
Authentication API Routes - JWT-based authentication endpoints
Enterprise authentication API for 3-day development plan
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, validator

from ..core.auth import auth_manager, get_current_user, get_current_admin_user
from ..core.database import db_manager, User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

# Request/Response Models
class UserRegistration(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Username must be between 3 and 50 characters')
        if not v.isalnum() and '_' not in v:
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserProfile(BaseModel):
    full_name: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime]
    preferences: Dict[str, Any]

# Authentication Routes
@router.post("/register", response_model=TokenResponse)
async def register_user(user_data: UserRegistration):
    """Register a new user"""
    try:
        # Register user
        user = await auth_manager.register_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        
        # Create tokens
        token_data = {
            "sub": user.id,
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin
        }
        
        access_token = auth_manager.create_access_token(token_data)
        refresh_token = auth_manager.create_refresh_token(token_data)
        
        # Prepare user data for response
        user_response = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "created_at": user.created_at,
            "preferences": user.preferences or {}
        }
        
        logger.info(f"User registered successfully: {user.username}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=30 * 60,  # 30 minutes
            user=user_response
        )
        
    except Exception as e:
        logger.error(f"User registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=TokenResponse)
async def login_user(login_data: UserLogin):
    """Authenticate user and return tokens"""
    try:
        # Authenticate user
        user = await auth_manager.authenticate_user(
            username=login_data.username,
            password=login_data.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Create tokens
        token_data = {
            "sub": user.id,
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin
        }
        
        access_token = auth_manager.create_access_token(token_data)
        refresh_token = auth_manager.create_refresh_token(token_data)
        
        # Prepare user data for response
        user_response = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "created_at": user.created_at,
            "last_login": user.last_login,
            "preferences": user.preferences or {}
        }
        
        logger.info(f"User logged in successfully: {user.username}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=30 * 60,  # 30 minutes
            user=user_response
        )
        
    except Exception as e:
        logger.error(f"User login failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

@router.post("/refresh", response_model=Dict[str, Any])
async def refresh_token(refresh_data: RefreshTokenRequest):
    """Refresh access token"""
    try:
        access_token = await auth_manager.refresh_access_token(refresh_data.refresh_token)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 30 * 60  # 30 minutes
        }
        
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token"
        )

@router.post("/logout")
async def logout_user(current_user: User = Depends(get_current_user)):
    """Logout user and revoke token"""
    try:
        # In a real implementation, you would revoke the token
        # For now, we'll just log the logout
        logger.info(f"User logged out: {current_user.username}")
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

# User Profile Routes
@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
        preferences=current_user.preferences or {}
    )

@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    profile_data: UserProfile,
    current_user: User = Depends(get_current_user)
):
    """Update current user profile"""
    try:
        # Update user profile
        update_data = {}
        if profile_data.full_name is not None:
            update_data["full_name"] = profile_data.full_name
        if profile_data.preferences is not None:
            update_data["preferences"] = profile_data.preferences
        
        if update_data:
            async with db_manager.get_session() as session:
                # Build update query
                set_clauses = []
                params = {"user_id": current_user.id}
                
                for key, value in update_data.items():
                    set_clauses.append(f"{key} = :{key}")
                    params[key] = value
                
                query = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = :user_id"
                await session.execute(query, params)
                await session.commit()
                
                # Get updated user
                result = await session.execute(
                    "SELECT * FROM users WHERE id = :user_id",
                    {"user_id": current_user.id}
                )
                updated_user = result.first()
        else:
            updated_user = current_user
        
        logger.info(f"User profile updated: {current_user.username}")
        
        return UserResponse(
            id=updated_user.id,
            username=updated_user.username,
            email=updated_user.email,
            full_name=updated_user.full_name,
            is_active=updated_user.is_active,
            is_admin=updated_user.is_admin,
            created_at=updated_user.created_at,
            last_login=updated_user.last_login,
            preferences=updated_user.preferences or {}
        )
        
    except Exception as e:
        logger.error(f"Profile update failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user)
):
    """Change user password"""
    try:
        # Verify current password
        if not auth_manager.verify_password(password_data.current_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Validate new password strength
        if not auth_manager.validate_password_strength(password_data.new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password does not meet requirements"
            )
        
        # Hash new password
        new_password_hash = auth_manager.hash_password(password_data.new_password)
        
        # Update password in database
        async with db_manager.get_session() as session:
            await session.execute(
                "UPDATE users SET password_hash = :password_hash WHERE id = :user_id",
                {"password_hash": new_password_hash, "user_id": current_user.id}
            )
            await session.commit()
        
        logger.info(f"Password changed for user: {current_user.username}")
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )

# API Key Management
@router.post("/api-key")
async def generate_api_key(current_user: User = Depends(get_current_user)):
    """Generate API key for user"""
    try:
        api_key = auth_manager.generate_api_key(current_user.id)
        
        logger.info(f"API key generated for user: {current_user.username}")
        
        return {
            "api_key": api_key,
            "message": "API key generated successfully. Store it securely as it won't be shown again."
        }
        
    except Exception as e:
        logger.error(f"API key generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key generation failed"
        )

# Admin Routes
@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user)
):
    """List all users (admin only)"""
    try:
        async with db_manager.get_session() as session:
            result = await session.execute(
                "SELECT * FROM users ORDER BY created_at DESC LIMIT :limit OFFSET :skip",
                {"limit": limit, "skip": skip}
            )
            users = result.fetchall()
        
        return [
            UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                is_active=user.is_active,
                is_admin=user.is_admin,
                created_at=user.created_at,
                last_login=user.last_login,
                preferences=user.preferences or {}
            )
            for user in users
        ]
        
    except Exception as e:
        logger.error(f"User listing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list users"
        )

@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    is_active: bool,
    current_user: User = Depends(get_current_admin_user)
):
    """Update user active status (admin only)"""
    try:
        async with db_manager.get_session() as session:
            await session.execute(
                "UPDATE users SET is_active = :is_active WHERE id = :user_id",
                {"is_active": is_active, "user_id": user_id}
            )
            await session.commit()
        
        logger.info(f"User status updated: {user_id} -> active: {is_active}")
        
        return {"message": f"User {'activated' if is_active else 'deactivated'} successfully"}
        
    except Exception as e:
        logger.error(f"User status update failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user status"
        )

# Health Check
@router.get("/health")
async def auth_health_check():
    """Authentication system health check"""
    try:
        # Check database connection
        stats = await db_manager.get_system_stats()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected",
            "user_count": stats["users"]["total"],
            "active_users": stats["users"]["active"]
        }
        
    except Exception as e:
        logger.error(f"Auth health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication system unhealthy"
        ) 