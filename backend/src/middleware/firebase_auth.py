"""
Firebase Authentication Middleware
"""

from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import auth as firebase_auth
import structlog
from typing import Optional

logger = structlog.get_logger()

security = HTTPBearer()

class FirebaseAuthMiddleware:
    """Firebase authentication middleware"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, request: Request, call_next):
        # Skip auth for public endpoints
        if request.url.path in ["/", "/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Skip auth for auth endpoints
        if request.url.path.startswith("/auth/"):
            return await call_next(request)
        
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Missing or invalid authorization header"
            )
        
        token = auth_header.split(" ")[1]
        
        try:
            # Verify Firebase ID token
            decoded_token = firebase_auth.verify_id_token(token)
            request.state.user = decoded_token
            request.state.uid = decoded_token.get("uid")
            request.state.email = decoded_token.get("email")
            request.state.role = decoded_token.get("role", "patient")
            
            logger.info("User authenticated", uid=request.state.uid)
            
        except firebase_auth.InvalidIdTokenError:
            logger.warning("Invalid Firebase token")
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            logger.error("Authentication error", error=str(e))
            raise HTTPException(status_code=401, detail="Authentication failed")
        
        return await call_next(request)

async def get_current_user(request: Request) -> dict:
    """Get current authenticated user"""
    if not hasattr(request.state, 'user'):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return request.state.user

async def get_current_uid(request: Request) -> str:
    """Get current user UID"""
    if not hasattr(request.state, 'uid'):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return request.state.uid

async def require_role(required_role: str):
    """Require specific user role"""
    def role_checker(request: Request):
        if not hasattr(request.state, 'role'):
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        user_role = request.state.role
        if user_role != required_role and user_role != "admin":
            raise HTTPException(
                status_code=403, 
                detail=f"Requires {required_role} role"
            )
        return user_role
    
    return role_checker
