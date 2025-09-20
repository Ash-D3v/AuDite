"""
Authentication Router
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, EmailStr
from typing import Optional
import structlog
from src.middleware.firebase_auth import get_current_user, get_current_uid
from src.services.firebase_client import FirebaseClient

logger = structlog.get_logger()
router = APIRouter()

# Pydantic models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "patient"  # patient, doctor, admin

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserProfile(BaseModel):
    uid: str
    email: str
    full_name: str
    role: str
    created_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile

@router.post("/register", response_model=TokenResponse)
async def register_user(user_data: UserRegister):
    """Register a new user"""
    try:
        firebase_client = FirebaseClient()
        await firebase_client.initialize()
        
        # Create user in Firebase Auth
        user_record = firebase_client.auth.create_user(
            email=user_data.email,
            password=user_data.password,
            display_name=user_data.full_name
        )
        
        # Store additional user data in Firestore
        user_doc = {
            "uid": user_record.uid,
            "email": user_data.email,
            "full_name": user_data.full_name,
            "role": user_data.role,
            "created_at": firebase_client.db.SERVER_TIMESTAMP,
            "profile": {
                "age": None,
                "gender": None,
                "phone": None,
                "address": None
            }
        }
        
        firebase_client.get_document("users", user_record.uid).set(user_doc)
        
        # Generate custom token for immediate login
        custom_token = firebase_client.auth.create_custom_token(user_record.uid)
        
        return TokenResponse(
            access_token=custom_token.decode('utf-8'),
            user=UserProfile(
                uid=user_record.uid,
                email=user_data.email,
                full_name=user_data.full_name,
                role=user_data.role,
                created_at=str(user_doc["created_at"])
            )
        )
        
    except Exception as e:
        logger.error("User registration failed", error=str(e))
        raise HTTPException(status_code=400, detail="Registration failed")

@router.post("/login", response_model=TokenResponse)
async def login_user(login_data: UserLogin):
    """Login user and return token"""
    try:
        firebase_client = FirebaseClient()
        await firebase_client.initialize()
        
        # Verify user credentials
        user_record = firebase_client.auth.get_user_by_email(login_data.email)
        
        # Get user profile from Firestore
        user_doc = firebase_client.get_document("users", user_record.uid).get()
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        user_data = user_doc.to_dict()
        
        # Generate custom token
        custom_token = firebase_client.auth.create_custom_token(user_record.uid)
        
        return TokenResponse(
            access_token=custom_token.decode('utf-8'),
            user=UserProfile(
                uid=user_record.uid,
                email=user_data["email"],
                full_name=user_data["full_name"],
                role=user_data["role"],
                created_at=str(user_data["created_at"])
            )
        )
        
    except Exception as e:
        logger.error("User login failed", error=str(e))
        raise HTTPException(status_code=401, detail="Login failed")

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    try:
        firebase_client = FirebaseClient()
        await firebase_client.initialize()
        
        uid = current_user.get("uid")
        user_doc = firebase_client.get_document("users", uid).get()
        
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        user_data = user_doc.to_dict()
        
        return UserProfile(
            uid=uid,
            email=user_data["email"],
            full_name=user_data["full_name"],
            role=user_data["role"],
            created_at=str(user_data["created_at"])
        )
        
    except Exception as e:
        logger.error("Get user profile failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get user profile")

@router.put("/me", response_model=UserProfile)
async def update_user_profile(
    profile_update: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update current user profile"""
    try:
        firebase_client = FirebaseClient()
        await firebase_client.initialize()
        
        uid = current_user.get("uid")
        
        # Update user document
        firebase_client.get_document("users", uid).update(profile_update)
        
        # Get updated profile
        user_doc = firebase_client.get_document("users", uid).get()
        user_data = user_doc.to_dict()
        
        return UserProfile(
            uid=uid,
            email=user_data["email"],
            full_name=user_data["full_name"],
            role=user_data["role"],
            created_at=str(user_data["created_at"])
        )
        
    except Exception as e:
        logger.error("Update user profile failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update profile")

@router.delete("/logout")
async def logout_user(current_user: dict = Depends(get_current_user)):
    """Logout user (client-side token invalidation)"""
    return {"message": "Logged out successfully"}
