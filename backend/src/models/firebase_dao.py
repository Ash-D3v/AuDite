"""
Firebase Data Access Objects (DAO)
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import structlog
from src.services.firebase_client import FirebaseClient
from src.models.pydantic_schemas import (
    UserCreate, UserUpdate, UserResponse,
    PatientCreate, PatientUpdate, PatientResponse,
    DietChartCreate, DietChartUpdate, DietChartResponse
)

logger = structlog.get_logger()

class UserDAO:
    """User Data Access Object"""
    
    def __init__(self, firebase_client: FirebaseClient):
        self.firebase_client = firebase_client
        self.collection = "users"
    
    async def create_user(self, user_data: UserCreate, uid: str) -> UserResponse:
        """Create a new user"""
        try:
            user_doc = {
                "uid": uid,
                "email": user_data.email,
                "full_name": user_data.full_name,
                "role": user_data.role.value,
                "created_at": self.firebase_client.db.SERVER_TIMESTAMP,
                "updated_at": self.firebase_client.db.SERVER_TIMESTAMP,
                "profile": {
                    "phone": None,
                    "address": None,
                    "age": None,
                    "gender": None
                }
            }
            
            self.firebase_client.get_document(self.collection, uid).set(user_doc)
            
            return UserResponse(
                uid=uid,
                email=user_data.email,
                full_name=user_data.full_name,
                role=user_data.role,
                created_at=user_doc["created_at"],
                updated_at=user_doc["updated_at"]
            )
            
        except Exception as e:
            logger.error("Create user failed", error=str(e))
            raise
    
    async def get_user(self, uid: str) -> Optional[UserResponse]:
        """Get user by UID"""
        try:
            doc = self.firebase_client.get_document(self.collection, uid).get()
            
            if not doc.exists:
                return None
            
            data = doc.to_dict()
            return UserResponse(
                uid=uid,
                email=data["email"],
                full_name=data["full_name"],
                role=data["role"],
                created_at=data["created_at"],
                updated_at=data["updated_at"]
            )
            
        except Exception as e:
            logger.error("Get user failed", error=str(e))
            raise
    
    async def update_user(self, uid: str, user_update: UserUpdate) -> Optional[UserResponse]:
        """Update user"""
        try:
            update_data = user_update.dict(exclude_unset=True)
            update_data["updated_at"] = self.firebase_client.db.SERVER_TIMESTAMP
            
            self.firebase_client.get_document(self.collection, uid).update(update_data)
            
            return await self.get_user(uid)
            
        except Exception as e:
            logger.error("Update user failed", error=str(e))
            raise
    
    async def delete_user(self, uid: str) -> bool:
        """Delete user (soft delete)"""
        try:
            self.firebase_client.get_document(self.collection, uid).update({
                "deleted": True,
                "deleted_at": self.firebase_client.db.SERVER_TIMESTAMP
            })
            return True
            
        except Exception as e:
            logger.error("Delete user failed", error=str(e))
            raise

class PatientDAO:
    """Patient Data Access Object"""
    
    def __init__(self, firebase_client: FirebaseClient):
        self.firebase_client = firebase_client
        self.collection = "patients"
    
    async def create_patient(self, patient_data: PatientCreate, assigned_doctor: str) -> PatientResponse:
        """Create a new patient"""
        try:
            patient_doc = {
                "full_name": patient_data.full_name,
                "email": patient_data.email,
                "phone": patient_data.phone,
                "age": patient_data.age,
                "gender": patient_data.gender.value,
                "address": patient_data.address,
                "medical_history": patient_data.medical_history or {},
                "dietary_preferences": patient_data.dietary_preferences or [],
                "current_medications": patient_data.current_medications or [],
                "prakriti_analysis": None,
                "assigned_doctor": assigned_doctor,
                "created_at": self.firebase_client.db.SERVER_TIMESTAMP,
                "updated_at": self.firebase_client.db.SERVER_TIMESTAMP
            }
            
            doc_ref = self.firebase_client.get_collection(self.collection).add(patient_doc)
            patient_id = doc_ref[1].id
            
            # Update with patient_id
            self.firebase_client.get_document(self.collection, patient_id).update({
                "patient_id": patient_id
            })
            
            return PatientResponse(
                patient_id=patient_id,
                full_name=patient_data.full_name,
                email=patient_data.email,
                phone=patient_data.phone,
                age=patient_data.age,
                gender=patient_data.gender,
                address=patient_data.address,
                medical_history=patient_data.medical_history,
                dietary_preferences=patient_data.dietary_preferences,
                current_medications=patient_data.current_medications,
                prakriti_analysis=None,
                assigned_doctor=assigned_doctor,
                created_at=patient_doc["created_at"],
                updated_at=patient_doc["updated_at"]
            )
            
        except Exception as e:
            logger.error("Create patient failed", error=str(e))
            raise
    
    async def get_patient(self, patient_id: str) -> Optional[PatientResponse]:
        """Get patient by ID"""
        try:
            doc = self.firebase_client.get_document(self.collection, patient_id).get()
            
            if not doc.exists:
                return None
            
            data = doc.to_dict()
            return PatientResponse(
                patient_id=patient_id,
                full_name=data["full_name"],
                email=data.get("email"),
                phone=data.get("phone"),
                age=data["age"],
                gender=data["gender"],
                address=data.get("address"),
                medical_history=data.get("medical_history"),
                dietary_preferences=data.get("dietary_preferences"),
                current_medications=data.get("current_medications"),
                prakriti_analysis=data.get("prakriti_analysis"),
                assigned_doctor=data.get("assigned_doctor"),
                created_at=data["created_at"],
                updated_at=data["updated_at"]
            )
            
        except Exception as e:
            logger.error("Get patient failed", error=str(e))
            raise
    
    async def update_patient(self, patient_id: str, patient_update: PatientUpdate) -> Optional[PatientResponse]:
        """Update patient"""
        try:
            update_data = patient_update.dict(exclude_unset=True)
            update_data["updated_at"] = self.firebase_client.db.SERVER_TIMESTAMP
            
            self.firebase_client.get_document(self.collection, patient_id).update(update_data)
            
            return await self.get_patient(patient_id)
            
        except Exception as e:
            logger.error("Update patient failed", error=str(e))
            raise
    
    async def list_patients(self, doctor_id: Optional[str] = None, skip: int = 0, limit: int = 10) -> List[PatientResponse]:
        """List patients with optional filtering"""
        try:
            query = self.firebase_client.get_collection(self.collection)
            
            if doctor_id:
                query = query.where("assigned_doctor", "==", doctor_id)
            
            docs = query.offset(skip).limit(limit).stream()
            
            patients = []
            for doc in docs:
                data = doc.to_dict()
                patients.append(PatientResponse(
                    patient_id=doc.id,
                    full_name=data["full_name"],
                    email=data.get("email"),
                    phone=data.get("phone"),
                    age=data["age"],
                    gender=data["gender"],
                    address=data.get("address"),
                    medical_history=data.get("medical_history"),
                    dietary_preferences=data.get("dietary_preferences"),
                    current_medications=data.get("current_medications"),
                    prakriti_analysis=data.get("prakriti_analysis"),
                    assigned_doctor=data.get("assigned_doctor"),
                    created_at=data["created_at"],
                    updated_at=data["updated_at"]
                ))
            
            return patients
            
        except Exception as e:
            logger.error("List patients failed", error=str(e))
            raise
    
    async def delete_patient(self, patient_id: str) -> bool:
        """Delete patient (soft delete)"""
        try:
            self.firebase_client.get_document(self.collection, patient_id).update({
                "deleted": True,
                "deleted_at": self.firebase_client.db.SERVER_TIMESTAMP
            })
            return True
            
        except Exception as e:
            logger.error("Delete patient failed", error=str(e))
            raise

class DietChartDAO:
    """Diet Chart Data Access Object"""
    
    def __init__(self, firebase_client: FirebaseClient):
        self.firebase_client = firebase_client
        self.collection = "diet_charts"
    
    async def create_diet_chart(self, chart_data: DietChartCreate, created_by: str) -> DietChartResponse:
        """Create a new diet chart"""
        try:
            chart_doc = {
                "patient_id": chart_data.patient_id,
                "created_by": created_by,
                "duration_days": chart_data.duration_days,
                "meals": [meal.dict() for meal in chart_data.meals],
                "total_nutrition": {},
                "ayurvedic_compliance": 0.5,
                "notes": chart_data.notes,
                "created_at": self.firebase_client.db.SERVER_TIMESTAMP,
                "updated_at": self.firebase_client.db.SERVER_TIMESTAMP
            }
            
            doc_ref = self.firebase_client.get_collection(self.collection).add(chart_doc)
            chart_id = doc_ref[1].id
            
            # Update with chart_id
            self.firebase_client.get_document(self.collection, chart_id).update({
                "chart_id": chart_id
            })
            
            return DietChartResponse(
                chart_id=chart_id,
                patient_id=chart_data.patient_id,
                created_by=created_by,
                duration_days=chart_data.duration_days,
                meals=chart_doc["meals"],
                total_nutrition=chart_doc["total_nutrition"],
                ayurvedic_compliance=chart_doc["ayurvedic_compliance"],
                notes=chart_data.notes,
                created_at=chart_doc["created_at"],
                updated_at=chart_doc["updated_at"]
            )
            
        except Exception as e:
            logger.error("Create diet chart failed", error=str(e))
            raise
    
    async def get_diet_chart(self, chart_id: str) -> Optional[DietChartResponse]:
        """Get diet chart by ID"""
        try:
            doc = self.firebase_client.get_document(self.collection, chart_id).get()
            
            if not doc.exists:
                return None
            
            data = doc.to_dict()
            return DietChartResponse(
                chart_id=chart_id,
                patient_id=data["patient_id"],
                created_by=data["created_by"],
                duration_days=data["duration_days"],
                meals=data["meals"],
                total_nutrition=data["total_nutrition"],
                ayurvedic_compliance=data["ayurvedic_compliance"],
                notes=data.get("notes"),
                created_at=data["created_at"],
                updated_at=data["updated_at"]
            )
            
        except Exception as e:
            logger.error("Get diet chart failed", error=str(e))
            raise
    
    async def update_diet_chart(self, chart_id: str, chart_update: DietChartUpdate) -> Optional[DietChartResponse]:
        """Update diet chart"""
        try:
            update_data = chart_update.dict(exclude_unset=True)
            update_data["updated_at"] = self.firebase_client.db.SERVER_TIMESTAMP
            
            self.firebase_client.get_document(self.collection, chart_id).update(update_data)
            
            return await self.get_diet_chart(chart_id)
            
        except Exception as e:
            logger.error("Update diet chart failed", error=str(e))
            raise
    
    async def list_diet_charts(self, patient_id: Optional[str] = None, created_by: Optional[str] = None, 
                              skip: int = 0, limit: int = 10) -> List[DietChartResponse]:
        """List diet charts with optional filtering"""
        try:
            query = self.firebase_client.get_collection(self.collection)
            
            if patient_id:
                query = query.where("patient_id", "==", patient_id)
            if created_by:
                query = query.where("created_by", "==", created_by)
            
            docs = query.offset(skip).limit(limit).order_by("created_at", direction="DESCENDING").stream()
            
            charts = []
            for doc in docs:
                data = doc.to_dict()
                charts.append(DietChartResponse(
                    chart_id=doc.id,
                    patient_id=data["patient_id"],
                    created_by=data["created_by"],
                    duration_days=data["duration_days"],
                    meals=data["meals"],
                    total_nutrition=data["total_nutrition"],
                    ayurvedic_compliance=data["ayurvedic_compliance"],
                    notes=data.get("notes"),
                    created_at=data["created_at"],
                    updated_at=data["updated_at"]
                ))
            
            return charts
            
        except Exception as e:
            logger.error("List diet charts failed", error=str(e))
            raise
    
    async def delete_diet_chart(self, chart_id: str) -> bool:
        """Delete diet chart (soft delete)"""
        try:
            self.firebase_client.get_document(self.collection, chart_id).update({
                "deleted": True,
                "deleted_at": self.firebase_client.db.SERVER_TIMESTAMP
            })
            return True
            
        except Exception as e:
            logger.error("Delete diet chart failed", error=str(e))
            raise
