"""
Diet Management Router
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import structlog
from src.middleware.firebase_auth import get_current_user, get_current_uid, require_role
from src.services.firebase_client import FirebaseClient
from src.services.ml.dosha_classifier import DoshaClassifier
from src.services.ml.compat_gnn import CompatibilityGNN
from src.services.ml.rasa_recommender import RasaRecommender
from src.services.ml.nutrient_calculator import NutrientCalculator
from src.services.ayurvedic.guna_calculator import GunaCalculator
from src.services.ayurvedic.viruddha_ahara import ViruddhaAharaDetector
from src.services.ayurvedic.agni_analyzer import AgniAnalyzer

logger = structlog.get_logger()
router = APIRouter()

# Pydantic models
class FoodItem(BaseModel):
    name: str
    quantity: float
    unit: str = "grams"
    meal_type: str  # breakfast, lunch, dinner, snack

class Meal(BaseModel):
    meal_type: str
    foods: List[FoodItem]
    timing: Optional[str] = None

class DietChartCreate(BaseModel):
    patient_id: str
    duration_days: int = 7
    meals: List[Meal]
    notes: Optional[str] = None

class DietChartResponse(BaseModel):
    chart_id: str
    patient_id: str
    created_by: str
    duration_days: int
    meals: List[Dict[str, Any]]
    total_nutrition: Dict[str, Any]
    ayurvedic_compliance: float
    created_at: str
    updated_at: str

class FoodAnalysisRequest(BaseModel):
    foods: List[FoodItem]

class FoodAnalysisResponse(BaseModel):
    compatibility_check: Dict[str, Any]
    rasa_analysis: Dict[str, Any]
    guna_analysis: Dict[str, Any]
    nutrition_analysis: Dict[str, Any]
    incompatibility_check: Dict[str, Any]
    agni_impact: Dict[str, Any]

class AgniPredictionRequest(BaseModel):
    historical_data: List[Dict[str, Any]]
    current_agni: Optional[float] = None

class AgniPredictionResponse(BaseModel):
    agni_score: float
    trend_direction: str
    confidence: float
    prediction_date: str
    recommendations: List[str]
    next_week_forecast: List[Dict[str, Any]]
    ml_model_used: str
    model_accuracy: str

@router.post("/analyze-prakriti", response_model=Dict[str, Any])
async def analyze_prakriti(
    analysis_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Analyze patient's Prakriti for diet recommendations"""
    try:
        dosha_classifier = DoshaClassifier()
        
        # Extract features from analysis data
        features = dosha_classifier.analyze_patient_features(analysis_data)
        dosha_analysis = dosha_classifier.predict_dosha(features)
        
        # Get rasa recommendations
        rasa_recommender = RasaRecommender()
        rasa_recommendations = rasa_recommender.recommend_rasas(
            dosha_analysis.get('dosha_scores', {}),
            analysis_data.get('current_rasas', [])
        )
        
        # Get guna recommendations
        guna_calculator = GunaCalculator()
        guna_recommendations = guna_calculator.recommend_guna_for_dosha(
            dosha_analysis.get('dosha_scores', {}),
            analysis_data.get('current_gunas', [])
        )
        
        return {
            "dosha_analysis": dosha_analysis,
            "rasa_recommendations": rasa_recommendations,
            "guna_recommendations": guna_recommendations,
            "diet_guidelines": {
                "primary_dosha": dosha_analysis.get('primary_dosha'),
                "recommended_foods": guna_recommendations.get('food_recommendations', {}),
                "avoid_foods": guna_recommendations.get('avoid_gunas', [])
            }
        }
        
    except Exception as e:
        logger.error("Prakriti analysis failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to analyze prakriti")

@router.post("/analyze-foods", response_model=FoodAnalysisResponse)
async def analyze_foods(
    analysis_request: FoodAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """Comprehensive analysis of food items"""
    try:
        foods = [food.dict() for food in analysis_request.foods]
        food_names = [food['name'] for food in foods]
        
        # Initialize analyzers
        compat_gnn = CompatibilityGNN()
        rasa_recommender = RasaRecommender()
        guna_calculator = GunaCalculator()
        nutrient_calculator = NutrientCalculator()
        incompatibility_detector = ViruddhaAharaDetector()
        agni_analyzer = AgniAnalyzer()
        
        # Perform analyses
        compatibility_result = compat_gnn.check_meal_compatibility(food_names)
        rasa_result = rasa_recommender.analyze_meal_rasas(foods)
        guna_result = guna_calculator.analyze_meal_guna(foods)
        nutrition_result = nutrient_calculator.calculate_meal_nutrition(foods)
        incompatibility_result = incompatibility_detector.check_meal_incompatibilities(food_names)
        
        # Agni impact (simplified - would need patient data)
        agni_result = {
            "agni_impact": "neutral",
            "recommendations": ["Consider your digestive capacity"]
        }
        
        return FoodAnalysisResponse(
            compatibility_check=compatibility_result,
            rasa_analysis=rasa_result,
            guna_analysis=guna_result,
            nutrition_analysis=nutrition_result,
            incompatibility_check=incompatibility_result,
            agni_impact=agni_result
        )
        
    except Exception as e:
        logger.error("Food analysis failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to analyze foods")

@router.post("/predict-agni-trend", response_model=AgniPredictionResponse)
async def predict_agni_trend(
    prediction_request: AgniPredictionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Predict Agni trend using LSTM time series model"""
    try:
        agni_analyzer = AgniAnalyzer()
        
        # Predict Agni trend using LSTM model
        prediction = agni_analyzer.predict_agni_trend(prediction_request.historical_data)
        
        return AgniPredictionResponse(
            agni_score=prediction.get('agni_score', 0.5),
            trend_direction=prediction.get('trend_direction', 'stable'),
            confidence=prediction.get('confidence', 0.5),
            prediction_date=prediction.get('prediction_date', ''),
            recommendations=prediction.get('recommendations', []),
            next_week_forecast=prediction.get('next_week_forecast', []),
            ml_model_used=prediction.get('ml_model_used', 'LSTM Time Series'),
            model_accuracy=prediction.get('model_accuracy', '88.2%')
        )
        
    except Exception as e:
        logger.error("Agni trend prediction failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to predict Agni trend")

@router.post("/assess-daily-agni", response_model=Dict[str, Any])
async def assess_daily_agni_with_ml(
    daily_metrics: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Assess daily Agni using ML model"""
    try:
        agni_analyzer = AgniAnalyzer()
        
        # Assess daily Agni using LSTM model
        assessment = agni_analyzer.assess_daily_agni_with_ml(daily_metrics)
        
        return assessment
        
    except Exception as e:
        logger.error("Daily Agni assessment failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to assess daily Agni")

@router.post("/predict-meal-agni-impact", response_model=Dict[str, Any])
async def predict_meal_agni_impact(
    meal_foods: List[Dict[str, Any]],
    current_agni: float,
    current_user: dict = Depends(get_current_user)
):
    """Predict how a meal will impact current Agni using ML model"""
    try:
        agni_analyzer = AgniAnalyzer()
        
        # Predict meal Agni impact using LSTM model
        prediction = agni_analyzer.predict_meal_agni_impact_with_ml(meal_foods, current_agni)
        
        return prediction
        
    except Exception as e:
        logger.error("Meal Agni impact prediction failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to predict meal Agni impact")

@router.post("/generate", response_model=DietChartResponse)
async def generate_diet_chart(
    chart_data: DietChartCreate,
    current_user: dict = Depends(get_current_user)
):
    """Generate AI-powered diet chart"""
    try:
        firebase_client = FirebaseClient()
        await firebase_client.initialize()
        
        # Check permissions
        user_role = current_user.get("role", "patient")
        if user_role not in ["doctor", "admin"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Get patient data
        patient_doc = firebase_client.get_document("patients", chart_data.patient_id).get()
        if not patient_doc.exists:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        patient_data = patient_doc.to_dict()
        dosha_scores = patient_data.get('prakriti_analysis', {}).get('dosha_scores', {})
        
        # Analyze and optimize meals
        optimized_meals = []
        total_nutrition = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'fiber': 0}
        
        for meal in chart_data.meals:
            # Analyze meal
            food_analysis = await analyze_foods(
                FoodAnalysisRequest(foods=meal.foods),
                current_user
            )
            
            # Calculate nutrition
            meal_nutrition = food_analysis.nutrition_analysis
            for nutrient, value in meal_nutrition.items():
                if nutrient in total_nutrition:
                    total_nutrition[nutrient] += value
            
            # Add analysis to meal
            meal_data = meal.dict()
            meal_data['analysis'] = food_analysis.dict()
            meal_data['nutrition'] = meal_nutrition
            optimized_meals.append(meal_data)
        
        # Calculate Ayurvedic compliance score
        compliance_score = _calculate_ayurvedic_compliance(optimized_meals, dosha_scores)
        
        # Create diet chart document
        chart_doc = {
            "patient_id": chart_data.patient_id,
            "created_by": current_user.get("uid"),
            "duration_days": chart_data.duration_days,
            "meals": optimized_meals,
            "total_nutrition": total_nutrition,
            "ayurvedic_compliance": compliance_score,
            "notes": chart_data.notes,
            "created_at": firebase_client.db.SERVER_TIMESTAMP,
            "updated_at": firebase_client.db.SERVER_TIMESTAMP
        }
        
        # Save to Firestore
        doc_ref = firebase_client.get_collection("diet_charts").add(chart_doc)
        chart_id = doc_ref[1].id
        
        # Update with chart_id
        firebase_client.get_document("diet_charts", chart_id).update({"chart_id": chart_id})
        
        logger.info("Diet chart generated", chart_id=chart_id, patient_id=chart_data.patient_id)
        
        return DietChartResponse(
            chart_id=chart_id,
            **chart_doc,
            created_at=str(chart_doc["created_at"]),
            updated_at=str(chart_doc["updated_at"])
        )
        
    except Exception as e:
        logger.error("Diet chart generation failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate diet chart")

@router.get("/charts/{chart_id}", response_model=DietChartResponse)
async def get_diet_chart(
    chart_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get diet chart by ID"""
    try:
        firebase_client = FirebaseClient()
        await firebase_client.initialize()
        
        # Get chart document
        chart_doc = firebase_client.get_document("diet_charts", chart_id).get()
        if not chart_doc.exists:
            raise HTTPException(status_code=404, detail="Diet chart not found")
        
        chart_data = chart_doc.to_dict()
        
        # Check permissions
        user_role = current_user.get("role", "patient")
        if user_role == "patient" and chart_data.get("patient_id") != current_user.get("uid"):
            raise HTTPException(status_code=403, detail="Access denied")
        elif user_role == "doctor" and chart_data.get("created_by") != current_user.get("uid"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return DietChartResponse(
            chart_id=chart_id,
            **chart_data,
            created_at=str(chart_data.get("created_at", "")),
            updated_at=str(chart_data.get("updated_at", ""))
        )
        
    except Exception as e:
        logger.error("Get diet chart failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get diet chart")

@router.get("/charts", response_model=List[DietChartResponse])
async def list_diet_charts(
    patient_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """List diet charts"""
    try:
        firebase_client = FirebaseClient()
        await firebase_client.initialize()
        
        # Build query
        query = firebase_client.get_collection("diet_charts")
        
        user_role = current_user.get("role", "patient")
        if user_role == "patient":
            query = query.where("patient_id", "==", current_user.get("uid"))
        elif user_role == "doctor":
            query = query.where("created_by", "==", current_user.get("uid"))
        
        if patient_id:
            query = query.where("patient_id", "==", patient_id)
        
        # Apply pagination
        docs = query.offset(skip).limit(limit).order_by("created_at", direction="DESCENDING").stream()
        
        charts = []
        for doc in docs:
            chart_data = doc.to_dict()
            charts.append(DietChartResponse(
                chart_id=doc.id,
                **chart_data,
                created_at=str(chart_data.get("created_at", "")),
                updated_at=str(chart_data.get("updated_at", ""))
            ))
        
        return charts
        
    except Exception as e:
        logger.error("List diet charts failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list diet charts")

@router.put("/charts/{chart_id}", response_model=DietChartResponse)
async def update_diet_chart(
    chart_id: str,
    chart_update: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Update diet chart"""
    try:
        firebase_client = FirebaseClient()
        await firebase_client.initialize()
        
        # Check if chart exists
        chart_doc = firebase_client.get_document("diet_charts", chart_id).get()
        if not chart_doc.exists:
            raise HTTPException(status_code=404, detail="Diet chart not found")
        
        chart_data = chart_doc.to_dict()
        
        # Check permissions
        user_role = current_user.get("role", "patient")
        if user_role == "patient" and chart_data.get("patient_id") != current_user.get("uid"):
            raise HTTPException(status_code=403, detail="Access denied")
        elif user_role == "doctor" and chart_data.get("created_by") != current_user.get("uid"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update chart
        update_data = chart_update.copy()
        update_data["updated_at"] = firebase_client.db.SERVER_TIMESTAMP
        
        firebase_client.get_document("diet_charts", chart_id).update(update_data)
        
        # Get updated chart
        updated_doc = firebase_client.get_document("diet_charts", chart_id).get()
        updated_data = updated_doc.to_dict()
        
        return DietChartResponse(
            chart_id=chart_id,
            **updated_data,
            created_at=str(updated_data.get("created_at", "")),
            updated_at=str(updated_data.get("updated_at", ""))
        )
        
    except Exception as e:
        logger.error("Update diet chart failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update diet chart")

@router.post("/charts/{chart_id}/clone", response_model=DietChartResponse)
async def clone_diet_chart(
    chart_id: str,
    new_patient_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Clone diet chart for another patient"""
    try:
        firebase_client = FirebaseClient()
        await firebase_client.initialize()
        
        # Get original chart
        original_doc = firebase_client.get_document("diet_charts", chart_id).get()
        if not original_doc.exists:
            raise HTTPException(status_code=404, detail="Diet chart not found")
        
        original_data = original_doc.to_dict()
        
        # Check permissions
        user_role = current_user.get("role", "patient")
        if user_role not in ["doctor", "admin"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Create cloned chart
        cloned_data = original_data.copy()
        cloned_data.update({
            "patient_id": new_patient_id,
            "created_by": current_user.get("uid"),
            "created_at": firebase_client.db.SERVER_TIMESTAMP,
            "updated_at": firebase_client.db.SERVER_TIMESTAMP
        })
        
        # Remove original chart_id
        if "chart_id" in cloned_data:
            del cloned_data["chart_id"]
        
        # Save cloned chart
        doc_ref = firebase_client.get_collection("diet_charts").add(cloned_data)
        new_chart_id = doc_ref[1].id
        
        firebase_client.get_document("diet_charts", new_chart_id).update({"chart_id": new_chart_id})
        
        logger.info("Diet chart cloned", original_id=chart_id, new_id=new_chart_id)
        
        return DietChartResponse(
            chart_id=new_chart_id,
            **cloned_data,
            created_at=str(cloned_data["created_at"]),
            updated_at=str(cloned_data["updated_at"])
        )
        
    except Exception as e:
        logger.error("Clone diet chart failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to clone diet chart")

def _calculate_ayurvedic_compliance(meals: List[Dict], dosha_scores: Dict[str, float]) -> float:
    """Calculate Ayurvedic compliance score for meals"""
    try:
        if not dosha_scores:
            return 0.5  # Neutral score if no dosha data
        
        primary_dosha = max(dosha_scores, key=dosha_scores.get)
        compliance_scores = []
        
        for meal in meals:
            meal_score = 0.5  # Base score
            
            # Check food compatibility
            if 'analysis' in meal and 'compatibility_check' in meal['analysis']:
                compat_score = meal['analysis']['compatibility_check'].get('score', 0.5)
                meal_score = (meal_score + compat_score) / 2
            
            # Check rasa balance
            if 'analysis' in meal and 'rasa_analysis' in meal['analysis']:
                rasa_score = meal['analysis']['rasa_analysis'].get('balance_score', 0.5)
                meal_score = (meal_score + rasa_score) / 2
            
            compliance_scores.append(meal_score)
        
        return sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0.5
        
    except Exception as e:
        logger.error("Compliance calculation failed", error=str(e))
        return 0.5
