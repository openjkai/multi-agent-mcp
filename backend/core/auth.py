"""
Authentication System - JWT-based auth with role management
Enterprise authentication for 3-day development plan
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets
import hashlib

from .database import db_manager, User

logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = "your-secret-key-change-in-production-please"  # Should be from environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer scheme
security = HTTPBearer()

class AuthenticationError(Exception):
    """Custom authentication error"""
    pass

class AuthorizationError(Exception):
    """Custom authorization error"""
    pass

class TokenData:
    """Token data structure"""
    def __init__(self, user_id: str, username: str, email: str, is_admin: bool = False):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.is_admin = is_admin

class AuthManager:
    """Authentication and authorization manager"""
    
    def __init__(self):
        self.active_tokens: Dict[str, TokenData] = {}
        self.blacklisted_tokens: set = set()
        self.failed_attempts: Dict[str, List[datetime]] = {}
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=15)
    
    def hash_password(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        # Store token data
        token_data = TokenData(
            user_id=data.get("sub"),
            username=data.get("username"),
            email=data.get("email"),
            is_admin=data.get("is_admin", False)
        )
        self.active_tokens[encoded_jwt] = token_data
        
        return encoded_jwt
    
    def create_refresh_token(self, data: dict) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    def verify_token(self, token: str) -> TokenData:
        """Verify and decode JWT token"""
        try:
            # Check if token is blacklisted
            if token in self.blacklisted_tokens:
                raise AuthenticationError("Token has been revoked")
            
            # Decode token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            
            if user_id is None:
                raise AuthenticationError("Invalid token")
            
            # Check token type
            token_type = payload.get("type", "access")
            if token_type != "access":
                raise AuthenticationError("Invalid token type")
            
            # Return token data
            return TokenData(
                user_id=user_id,
                username=payload.get("username"),
                email=payload.get("email"),
                is_admin=payload.get("is_admin", False)
            )
            
        except JWTError as e:
            logger.error(f"JWT verification failed: {str(e)}")
            raise AuthenticationError("Could not validate credentials")
    
    def revoke_token(self, token: str):
        """Revoke a token"""
        self.blacklisted_tokens.add(token)
        if token in self.active_tokens:
            del self.active_tokens[token]
    
    def is_account_locked(self, identifier: str) -> bool:
        """Check if account is locked due to failed attempts"""
        if identifier not in self.failed_attempts:
            return False
        
        attempts = self.failed_attempts[identifier]
        recent_attempts = [
            attempt for attempt in attempts
            if datetime.utcnow() - attempt < self.lockout_duration
        ]
        
        return len(recent_attempts) >= self.max_failed_attempts
    
    def record_failed_attempt(self, identifier: str):
        """Record a failed login attempt"""
        if identifier not in self.failed_attempts:
            self.failed_attempts[identifier] = []
        
        self.failed_attempts[identifier].append(datetime.utcnow())
        
        # Clean old attempts
        cutoff = datetime.utcnow() - self.lockout_duration
        self.failed_attempts[identifier] = [
            attempt for attempt in self.failed_attempts[identifier]
            if attempt > cutoff
        ]
    
    def clear_failed_attempts(self, identifier: str):
        """Clear failed attempts for successful login"""
        if identifier in self.failed_attempts:
            del self.failed_attempts[identifier]
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username/password"""
        try:
            # Check if account is locked
            if self.is_account_locked(username):
                raise AuthenticationError("Account temporarily locked due to failed attempts")
            
            # Get user from database
            user = await db_manager.get_user_by_username(username)
            if not user:
                # Try email
                user = await db_manager.get_user_by_email(username)
            
            if not user:
                self.record_failed_attempt(username)
                raise AuthenticationError("Invalid credentials")
            
            # Verify password
            if not self.verify_password(password, user.password_hash):
                self.record_failed_attempt(username)
                raise AuthenticationError("Invalid credentials")
            
            # Check if user is active
            if not user.is_active:
                raise AuthenticationError("Account is disabled")
            
            # Clear failed attempts on successful login
            self.clear_failed_attempts(username)
            
            # Update last login
            async with db_manager.get_session() as session:
                await session.execute(
                    "UPDATE users SET last_login = :now WHERE id = :user_id",
                    {"now": datetime.utcnow(), "user_id": user.id}
                )
                await session.commit()
            
            return user
            
        except Exception as e:
            logger.error(f"Authentication failed for {username}: {str(e)}")
            raise
    
    async def register_user(self, username: str, email: str, password: str, full_name: str = None) -> User:
        """Register a new user"""
        try:
            # Check if username exists
            existing_user = await db_manager.get_user_by_username(username)
            if existing_user:
                raise AuthenticationError("Username already exists")
            
            # Check if email exists
            existing_email = await db_manager.get_user_by_email(email)
            if existing_email:
                raise AuthenticationError("Email already exists")
            
            # Validate password strength
            if not self.validate_password_strength(password):
                raise AuthenticationError("Password does not meet requirements")
            
            # Hash password
            password_hash = self.hash_password(password)
            
            # Create user
            user = await db_manager.create_user(
                username=username,
                email=email,
                password_hash=password_hash,
                full_name=full_name
            )
            
            logger.info(f"New user registered: {username}")
            return user
            
        except Exception as e:
            logger.error(f"User registration failed: {str(e)}")
            raise
    
    def validate_password_strength(self, password: str) -> bool:
        """Validate password strength"""
        if len(password) < 8:
            return False
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        return has_upper and has_lower and has_digit and has_special
    
    async def refresh_access_token(self, refresh_token: str) -> str:
        """Refresh access token using refresh token"""
        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # Check token type
            if payload.get("type") != "refresh":
                raise AuthenticationError("Invalid token type")
            
            user_id = payload.get("sub")
            if not user_id:
                raise AuthenticationError("Invalid token")
            
            # Get user from database
            async with db_manager.get_session() as session:
                result = await session.execute(
                    "SELECT * FROM users WHERE id = :user_id AND is_active = true",
                    {"user_id": user_id}
                )
                user = result.first()
            
            if not user:
                raise AuthenticationError("User not found or inactive")
            
            # Create new access token
            access_token_data = {
                "sub": user.id,
                "username": user.username,
                "email": user.email,
                "is_admin": user.is_admin
            }
            
            return self.create_access_token(access_token_data)
            
        except JWTError as e:
            logger.error(f"Token refresh failed: {str(e)}")
            raise AuthenticationError("Could not refresh token")
    
    def generate_api_key(self, user_id: str) -> str:
        """Generate API key for user"""
        # Create a unique API key
        random_part = secrets.token_urlsafe(32)
        user_part = hashlib.sha256(user_id.encode()).hexdigest()[:8]
        api_key = f"mcp_{user_part}_{random_part}"
        
        return api_key
    
    async def validate_api_key(self, api_key: str) -> Optional[User]:
        """Validate API key and return user"""
        try:
            if not api_key.startswith("mcp_"):
                return None
            
            # Extract user part
            parts = api_key.split("_")
            if len(parts) != 3:
                return None
            
            user_part = parts[1]
            
            # Find user by matching hash
            async with db_manager.get_session() as session:
                result = await session.execute("SELECT * FROM users WHERE is_active = true")
                users = result.fetchall()
                
                for user in users:
                    expected_hash = hashlib.sha256(user.id.encode()).hexdigest()[:8]
                    if expected_hash == user_part:
                        return user
            
            return None
            
        except Exception as e:
            logger.error(f"API key validation failed: {str(e)}")
            return None

# Global auth manager
auth_manager = AuthManager()

# Dependency functions for FastAPI
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user"""
    try:
        token = credentials.credentials
        token_data = auth_manager.verify_token(token)
        
        # Get user from database
        async with db_manager.get_session() as session:
            result = await session.execute(
                "SELECT * FROM users WHERE id = :user_id AND is_active = true",
                {"user_id": token_data.user_id}
            )
            user = result.first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        return user
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )

async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current admin user"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[User]:
    """Get current user if authenticated, None otherwise"""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None 