"""
Rate Limiting Middleware using Firestore
"""

from fastapi import Request, HTTPException
from datetime import datetime, timedelta
import asyncio
import structlog
from src.services.firebase_client import FirebaseClient
from src.config import settings

logger = structlog.get_logger()

class RateLimiterMiddleware:
    """Firestore-based rate limiting middleware"""
    
    def __init__(self, app):
        self.app = app
        self.firebase_client = FirebaseClient()
        self.rate_limit_requests = settings.RATE_LIMIT_REQUESTS
        self.rate_limit_window = settings.RATE_LIMIT_WINDOW
    
    async def __call__(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/"]:
            return await call_next(request)
        
        # Get user identifier
        user_id = getattr(request.state, 'uid', request.client.host)
        
        try:
            # Check rate limit
            is_allowed = await self._check_rate_limit(user_id)
            
            if not is_allowed:
                logger.warning("Rate limit exceeded", user_id=user_id)
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Please try again later."
                )
            
            # Increment request count
            await self._increment_request_count(user_id)
            
        except Exception as e:
            logger.error("Rate limiting error", error=str(e))
            # Continue without rate limiting if there's an error
        
        return await call_next(request)
    
    async def _check_rate_limit(self, user_id: str) -> bool:
        """Check if user is within rate limit"""
        try:
            # Get current request count from Firestore
            doc_ref = self.firebase_client.db.collection("rate_limits").document(user_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return True  # First request
            
            data = doc.to_dict()
            current_count = data.get("current_count", 0)
            reset_at = data.get("reset_at")
            
            # Check if window has expired
            if reset_at and datetime.utcnow() > reset_at:
                return True  # Window expired, reset allowed
            
            return current_count < self.rate_limit_requests
            
        except Exception as e:
            logger.error("Rate limit check failed", error=str(e))
            return True  # Allow request on error
    
    async def _increment_request_count(self, user_id: str):
        """Increment request count for user"""
        try:
            doc_ref = self.firebase_client.db.collection("rate_limits").document(user_id)
            
            # Use transaction to atomically increment
            @firebase_client.db.transaction
            def update_count(transaction):
                doc = doc_ref.get(transaction=transaction)
                
                if not doc.exists:
                    # First request in window
                    reset_at = datetime.utcnow() + timedelta(seconds=self.rate_limit_window)
                    transaction.set(doc_ref, {
                        "current_count": 1,
                        "reset_at": reset_at,
                        "created_at": datetime.utcnow()
                    })
                else:
                    data = doc.to_dict()
                    current_count = data.get("current_count", 0)
                    reset_at = data.get("reset_at")
                    
                    # Check if window has expired
                    if reset_at and datetime.utcnow() > reset_at:
                        # Reset window
                        new_reset_at = datetime.utcnow() + timedelta(seconds=self.rate_limit_window)
                        transaction.set(doc_ref, {
                            "current_count": 1,
                            "reset_at": new_reset_at,
                            "updated_at": datetime.utcnow()
                        })
                    else:
                        # Increment count
                        transaction.update(doc_ref, {
                            "current_count": current_count + 1,
                            "updated_at": datetime.utcnow()
                        })
            
            update_count()
            
        except Exception as e:
            logger.error("Failed to increment request count", error=str(e))
