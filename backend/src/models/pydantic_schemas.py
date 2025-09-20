"""
Pydantic Schemas for API Request/Response Models
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

# Enums
class UserRole(str, Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class MealType(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"

class DoshaType(str, Enum):
    VATA = "vata"
    PITTA = "pitta"
    KAPHA = "kapha"

class RasaType(str, Enum):
    SWEET = "sweet"
    SOUR = "sour"
    SALTY = "salty"
    PUNGENT = "pungent"
    BITTER = "bitter"
    ASTRINGENT = "astringent"

class GunaType(str, Enum):
    HOT = "hot"
    COLD = "cold"
    NEUTRAL = "neutral"

# Base Models
class BaseResponse(BaseModel):
    success: bool = True
    message: str = "Success"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# User Models
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.PATIENT

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class UserResponse(UserBase):
    uid: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Patient Models
class PatientBase(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    age: int = Field(..., ge=0, le=120)
    gender: Gender
    address: Optional[str] = None

class PatientCreate(PatientBase):
    medical_history: Optional[Dict[str, Any]] = None
    dietary_preferences: Optional[List[str]] = None
    current_medications: Optional[List[str]] = None

class PatientUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=120)
    gender: Optional[Gender] = None
    address: Optional[str] = None
    medical_history: Optional[Dict[str, Any]] = None
    dietary_preferences: Optional[List[str]] = None
    current_medications: Optional[List[str]] = None

class PatientResponse(PatientBase):
    patient_id: str
    prakriti_analysis: Optional[Dict[str, Any]] = None
    assigned_doctor: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Prakriti Analysis Models
class PrakritiAnalysisRequest(BaseModel):
    physical_characteristics: Dict[str, Any]
    mental_characteristics: Dict[str, Any]
    lifestyle_habits: Dict[str, Any]
    health_symptoms: Dict[str, Any]

class PrakritiAnalysisResponse(BaseModel):
    primary_dosha: DoshaType
    dosha_scores: Dict[str, float]
    confidence: float
    recommendations: Dict[str, Any]
    analysis_date: datetime = Field(default_factory=datetime.utcnow)

# Food Models
class FoodItem(BaseModel):
    name: str
    quantity: float = Field(..., gt=0)
    unit: str = "grams"
    meal_type: MealType

class FoodProperties(BaseModel):
    rasa: List[RasaType]
    guna: GunaType
    virya: str  # heating/cooling
    vipaka: str  # post-digestive effect
    prabhav: Optional[str] = None  # special effect

class NutritionalData(BaseModel):
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: float
    vitamins: Optional[Dict[str, float]] = None
    minerals: Optional[Dict[str, float]] = None

class FoodAnalysis(BaseModel):
    food_name: str
    ayurvedic_properties: FoodProperties
    nutritional_data: NutritionalData
    compatibility_score: float
    agni_impact: str

# Meal Models
class Meal(BaseModel):
    meal_type: MealType
    foods: List[FoodItem]
    timing: Optional[str] = None
    notes: Optional[str] = None

class MealAnalysis(BaseModel):
    compatibility_check: Dict[str, Any]
    rasa_analysis: Dict[str, Any]
    guna_analysis: Dict[str, Any]
    nutrition_analysis: Dict[str, Any]
    incompatibility_check: Dict[str, Any]
    agni_impact: Dict[str, Any]

# Diet Chart Models
class DietChartCreate(BaseModel):
    patient_id: str
    duration_days: int = Field(7, ge=1, le=365)
    meals: List[Meal]
    notes: Optional[str] = None
    include_analysis: bool = True

class DietChartUpdate(BaseModel):
    meals: Optional[List[Meal]] = None
    notes: Optional[str] = None
    duration_days: Optional[int] = Field(None, ge=1, le=365)

class DietChartResponse(BaseModel):
    chart_id: str
    patient_id: str
    created_by: str
    duration_days: int
    meals: List[Dict[str, Any]]
    total_nutrition: Dict[str, Any]
    ayurvedic_compliance: float
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Analytics Models
class ComplianceMetrics(BaseModel):
    overall_compliance: float
    meal_compliance: Dict[str, float]
    nutrition_balance: Dict[str, float]
    ayurvedic_adherence: float
    improvement_areas: List[str]

class PatientAnalytics(BaseModel):
    patient_id: str
    total_diet_charts: int
    avg_compliance: float
    recent_trends: Dict[str, Any]
    health_metrics: Dict[str, Any]
    recommendations: List[str]

# Report Models
class ReportRequest(BaseModel):
    chart_id: str
    include_analysis: bool = True
    include_nutrition: bool = True
    include_recommendations: bool = True
    format: str = "pdf"

class ReportResponse(BaseModel):
    report_id: str
    chart_id: str
    generated_at: datetime
    download_url: str
    format: str

# Search Models
class FoodSearchRequest(BaseModel):
    query: str
    cuisine_type: Optional[str] = None
    rasa: Optional[List[RasaType]] = None
    guna: Optional[GunaType] = None
    limit: int = Field(20, ge=1, le=100)

class FoodSearchResponse(BaseModel):
    foods: List[Dict[str, Any]]
    total_count: int
    page: int
    limit: int

# Validation Models
class ValidationError(BaseModel):
    field: str
    message: str
    value: Any

class ValidationResponse(BaseModel):
    valid: bool
    errors: List[ValidationError] = []

# Health Check Models
class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    version: str
    services: Dict[str, Any]

# Pagination Models
class PaginationParams(BaseModel):
    skip: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool

# Custom Validators
def validate_dosha_scores(scores: Dict[str, float]) -> Dict[str, float]:
    """Validate and normalize dosha scores"""
    total = sum(scores.values())
    if abs(total - 1.0) > 0.01:
        # Normalize scores
        return {k: v/total for k, v in scores.items()}
    return scores

def validate_meal_timing(timing: str) -> str:
    """Validate and format meal timing"""
    valid_timings = ["breakfast", "lunch", "dinner", "snack"]
    timing_lower = timing.lower()
    
    if timing_lower in valid_timings:
        return timing_lower
    
    # Map common variations
    timing_map = {
        "morning": "breakfast",
        "afternoon": "lunch",
        "evening": "dinner"
    }
    
    return timing_map.get(timing_lower, "breakfast")

# Add validators to models
class PrakritiAnalysisResponse(BaseModel):
    primary_dosha: DoshaType
    dosha_scores: Dict[str, float]
    confidence: float
    recommendations: Dict[str, Any]
    analysis_date: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('dosha_scores')
    def validate_dosha_scores(cls, v):
        return validate_dosha_scores(v)

class Meal(BaseModel):
    meal_type: MealType
    foods: List[FoodItem]
    timing: Optional[str] = None
    notes: Optional[str] = None
    
    @validator('timing')
    def validate_timing(cls, v):
        if v is None:
            return v
        return validate_meal_timing(v)
