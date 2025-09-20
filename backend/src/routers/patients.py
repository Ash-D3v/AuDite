"""
Patient Management Router
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
import structlog
from src.middleware.firebase_auth import get_current_user, get_current_uid, require_role
from src.services.firebase_client import FirebaseClient
from src.services.ml.dosha_classifier import DoshaClassifier

logger = structlog.get_logger()
router = APIRouter()

# Pydantic models
class PatientCreate(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    age: int
    gender: str
    address: Optional[str] = None
    medical_history: Optional[Dict[str, Any]] = None
    dietary_preferences: Optional[List[str]] = None
    current_medications: Optional[List[str]] = None

class PatientUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    medical_history: Optional[Dict[str, Any]] = None
    dietary_preferences: Optional[List[str]] = None
    current_medications: Optional[List[str]] = None

class PatientResponse(BaseModel):
    patient_id: str
    full_name: str
    email: Optional[str]
    phone: Optional[str]
    age: int
    gender: str
    address: Optional[str]
    medical_history: Optional[Dict[str, Any]]
    dietary_preferences: Optional[List[str]]
    current_medications: Optional[List[str]]
    prakriti_analysis: Optional[Dict[str, Any]]
    assigned_doctor: Optional[str]
    created_at: str
    updated_at: str

class PrakritiAnalysisRequest(BaseModel):
    symptoms: Dict[str, Any]
    physical_characteristics: Dict[str, Any]
    lifestyle_habits: Dict[str, Any]

@router.post("/", response_model=PatientResponse)
async def create_patient(
    patient_data: PatientCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new patient"""
    try:
        firebase_client = FirebaseClient()
        await firebase_client.initialize()
        
        # Check if user has permission to create patients
        user_role = current_user.get("role", "patient")
        if user_role not in ["doctor", "admin"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Create patient document
        patient_doc = {
            "full_name": patient_data.full_name,
            "email": patient_data.email,
            "phone": patient_data.phone,
            "age": patient_data.age,
            "gender": patient_data.gender,
            "address": patient_data.address,
            "medical_history": patient_data.medical_history or {},
            "dietary_preferences": patient_data.dietary_preferences or [],
            "current_medications": patient_data.current_medications or [],
            "prakriti_analysis": None,
            "assigned_doctor": current_user.get("uid"),
            "created_at": firebase_client.db.SERVER_TIMESTAMP,
            "updated_at": firebase_client.db.SERVER_TIMESTAMP
        }
        
        # Add to Firestore
        doc_ref = firebase_client.get_collection("patients").add(patient_doc)
        patient_id = doc_ref[1].id
        
        # Update with patient_id
        firebase_client.get_document("patients", patient_id).update({"patient_id": patient_id})
        
        logger.info("Patient created", patient_id=patient_id, doctor_uid=current_user.get("uid"))
        
        return PatientResponse(
            patient_id=patient_id,
            **patient_doc,
            created_at=str(patient_doc["created_at"]),
            updated_at=str(patient_doc["updated_at"])
        )
        
    except Exception as e:
        logger.error("Patient creation failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create patient")

@router.get("/", response_model=List[PatientResponse])
async def list_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """List patients (doctor/admin only)"""
    try:
        firebase_client = FirebaseClient()
        await firebase_client.initialize()
        
        user_role = current_user.get("role", "patient")
        if user_role not in ["doctor", "admin"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Query patients
        query = firebase_client.get_collection("patients")
        
        # If doctor, filter by assigned patients
        if user_role == "doctor":
            query = query.where("assigned_doctor", "==", current_user.get("uid"))
        
        # Apply pagination
        docs = query.offset(skip).limit(limit).stream()
        
        patients = []
        for doc in docs:
            patient_data = doc.to_dict()
            patients.append(PatientResponse(
                patient_id=doc.id,
                **patient_data,
                created_at=str(patient_data.get("created_at", "")),
                updated_at=str(patient_data.get("updated_at", ""))
            ))
        
        return patients
        
    except Exception as e:
        logger.error("List patients failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list patients")

@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get patient by ID"""
    try:
        firebase_client = FirebaseClient()
        await firebase_client.initialize()
        
        # Get patient document
        patient_doc = firebase_client.get_document("patients", patient_id).get()
        
        if not patient_doc.exists:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        patient_data = patient_doc.to_dict()
        
        # Check permissions
        user_role = current_user.get("role", "patient")
        if user_role == "patient" and current_user.get("uid") != patient_id:
            raise HTTPException(status_code=403, detail="Access denied")
        elif user_role == "doctor" and patient_data.get("assigned_doctor") != current_user.get("uid"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return PatientResponse(
            patient_id=patient_id,
            **patient_data,
            created_at=str(patient_data.get("created_at", "")),
            updated_at=str(patient_data.get("updated_at", ""))
        )
        
    except Exception as e:
        logger.error("Get patient failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get patient")

@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: str,
    patient_update: PatientUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update patient information"""
    try:
        firebase_client = FirebaseClient()
        await firebase_client.initialize()
        
        # Check if patient exists
        patient_doc = firebase_client.get_document("patients", patient_id).get()
        if not patient_doc.exists:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        patient_data = patient_doc.to_dict()
        
        # Check permissions
        user_role = current_user.get("role", "patient")
        if user_role == "patient" and current_user.get("uid") != patient_id:
            raise HTTPException(status_code=403, detail="Access denied")
        elif user_role == "doctor" and patient_data.get("assigned_doctor") != current_user.get("uid"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Prepare update data
        update_data = patient_update.dict(exclude_unset=True)
        update_data["updated_at"] = firebase_client.db.SERVER_TIMESTAMP
        
        # Update patient document
        firebase_client.get_document("patients", patient_id).update(update_data)
        
        # Get updated patient data
        updated_doc = firebase_client.get_document("patients", patient_id).get()
        updated_data = updated_doc.to_dict()
        
        return PatientResponse(
            patient_id=patient_id,
            **updated_data,
            created_at=str(updated_data.get("created_at", "")),
            updated_at=str(updated_data.get("updated_at", ""))
        )
        
    except Exception as e:
        logger.error("Update patient failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update patient")

@router.post("/{patient_id}/analyze-prakriti", response_model=Dict[str, Any])
async def analyze_prakriti(
    patient_id: str,
    analysis_request: PrakritiAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """Analyze patient's Prakriti (constitution)"""
    try:
        firebase_client = FirebaseClient()
        await firebase_client.initialize()
        
        # Check permissions
        user_role = current_user.get("role", "patient")
        if user_role == "patient" and current_user.get("uid") != patient_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get patient data
        patient_doc = firebase_client.get_document("patients", patient_id).get()
        if not patient_doc.exists:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        patient_data = patient_doc.to_dict()
        
        # Prepare features for dosha classification
        features = {
            'age': patient_data.get('age', 30),
            'gender': patient_data.get('gender', 'male'),
            **analysis_request.symptoms,
            **analysis_request.physical_characteristics,
            **analysis_request.lifestyle_habits
        }
        
        # Analyze dosha using ML model
        dosha_classifier = DoshaClassifier()
        feature_vector = dosha_classifier.analyze_patient_features(features)
        dosha_analysis = dosha_classifier.predict_dosha(feature_vector)
        
        # Update patient with prakriti analysis
        firebase_client.get_document("patients", patient_id).update({
            "prakriti_analysis": dosha_analysis,
            "updated_at": firebase_client.db.SERVER_TIMESTAMP
        })
        
        logger.info("Prakriti analysis completed", patient_id=patient_id, dosha=dosha_analysis.get('primary_dosha'))
        
        return dosha_analysis
        
    except Exception as e:
        logger.error("Prakriti analysis failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to analyze prakriti")

@router.delete("/{patient_id}")
async def delete_patient(
    patient_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Soft delete patient (admin only)"""
    try:
        firebase_client = FirebaseClient()
        await firebase_client.initialize()
        
        user_role = current_user.get("role", "patient")
        if user_role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Soft delete by adding deleted flag
        firebase_client.get_document("patients", patient_id).update({
            "deleted": True,
            "deleted_at": firebase_client.db.SERVER_TIMESTAMP,
            "deleted_by": current_user.get("uid"),
            "updated_at": firebase_client.db.SERVER_TIMESTAMP
        })
        
        logger.info("Patient soft deleted", patient_id=patient_id, deleted_by=current_user.get("uid"))
        
        return {"message": "Patient deleted successfully"}
        
    except Exception as e:
        logger.error("Delete patient failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to delete patient")
