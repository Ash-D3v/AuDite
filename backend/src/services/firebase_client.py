"""
Firebase Client Service
"""

import firebase_admin
from firebase_admin import credentials, firestore, storage
from google.cloud import storage as gcs
import structlog
from src.config import settings
import os

logger = structlog.get_logger()

class FirebaseClient:
    """Firebase client wrapper"""
    
    def __init__(self):
        self.db = None
        self.storage_client = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize Firebase services"""
        if self._initialized:
            return
        
        try:
            # Initialize Firebase Admin SDK
            if not firebase_admin._apps:
                cred_path = settings.FIREBASE_CRED_PATH
                if not os.path.exists(cred_path):
                    raise FileNotFoundError(f"Firebase credentials not found at {cred_path}")
                
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred, {
                    'projectId': settings.GOOGLE_CLOUD_PROJECT,
                    'storageBucket': f"{settings.GOOGLE_CLOUD_PROJECT}.appspot.com"
                })
            
            # Initialize Firestore
            self.db = firestore.client()
            
            # Initialize Cloud Storage
            self.storage_client = gcs.Client(project=settings.GOOGLE_CLOUD_PROJECT)
            
            self._initialized = True
            logger.info("Firebase initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize Firebase", error=str(e))
            raise
    
    async def health_check(self) -> bool:
        """Check Firebase connection health"""
        try:
            if not self._initialized:
                await self.initialize()
            
            # Test Firestore connection
            test_doc = self.db.collection("_health_check").document("test")
            test_doc.set({"timestamp": firestore.SERVER_TIMESTAMP})
            test_doc.delete()
            
            return True
            
        except Exception as e:
            logger.error("Firebase health check failed", error=str(e))
            return False
    
    def get_collection(self, collection_name: str):
        """Get Firestore collection reference"""
        if not self._initialized:
            raise RuntimeError("Firebase not initialized")
        return self.db.collection(f"{settings.FIRESTORE_COLLECTION_PREFIX}_{collection_name}")
    
    def get_document(self, collection_name: str, document_id: str):
        """Get Firestore document reference"""
        return self.get_collection(collection_name).document(document_id)
    
    async def upload_file(self, bucket_name: str, file_path: str, destination_blob_name: str):
        """Upload file to Cloud Storage"""
        try:
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(destination_blob_name)
            blob.upload_from_filename(file_path)
            return f"gs://{bucket_name}/{destination_blob_name}"
        except Exception as e:
            logger.error("File upload failed", error=str(e))
            raise
    
    async def download_file(self, bucket_name: str, source_blob_name: str, destination_file_name: str):
        """Download file from Cloud Storage"""
        try:
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(source_blob_name)
            blob.download_to_filename(destination_file_name)
            return destination_file_name
        except Exception as e:
            logger.error("File download failed", error=str(e))
            raise
