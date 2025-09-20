"""
Analytics Router
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import structlog
from src.middleware.firebase_auth import get_current_user, get_current_uid, require_role
from src.services.firebase_client import FirebaseClient

logger = structlog.get_logger()
router = APIRouter()

# Pydantic models
class PatientAnalytics(BaseModel):
    patient_id: str
    total_diet_charts: int
    avg_compliance: float
    recent_trends: Dict[str, Any]
    health_metrics: Dict[str, Any]
    recommendations: List[str]

class ComplianceMetrics(BaseModel):
    chart_id: str
    overall_compliance: float
    meal_compliance: Dict[str, float]
    nutrition_balance: Dict[str, float]
    ayurvedic_adherence: float
    improvement_areas: List[str]

@router.get("/patient/{patient_id}", response_model=PatientAnalytics)
async def get_patient_analytics(
    patient_id: str,
    days: int = Query(30, ge=7, le=365),
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive analytics for a patient"""
    try:
        firebase_client = FirebaseClient()
        await firebase_client.initialize()
        
        # Check permissions
        user_role = current_user.get("role", "patient")
        if user_role == "patient" and current_user.get("uid") != patient_id:
            raise HTTPException(status_code=403, detail="Access denied")
        elif user_role == "doctor":
            # Check if doctor is assigned to this patient
            patient_doc = firebase_client.get_document("patients", patient_id).get()
            if not patient_doc.exists:
                raise HTTPException(status_code=404, detail="Patient not found")
            patient_data = patient_doc.to_dict()
            if patient_data.get("assigned_doctor") != current_user.get("uid"):
                raise HTTPException(status_code=403, detail="Access denied")
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get diet charts for the period
        charts_query = firebase_client.get_collection("diet_charts").where(
            "patient_id", "==", patient_id
        ).where("created_at", ">=", start_date)
        
        charts = list(charts_query.stream())
        total_charts = len(charts)
        
        # Calculate compliance metrics
        compliance_scores = []
        for chart in charts:
            chart_data = chart.to_dict()
            compliance = chart_data.get("ayurvedic_compliance", 0.5)
            compliance_scores.append(compliance)
        
        avg_compliance = sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0.5
        
        # Analyze trends
        recent_trends = _analyze_compliance_trends(charts)
        
        # Get health metrics (simplified)
        health_metrics = _calculate_health_metrics(charts)
        
        # Generate recommendations
        recommendations = _generate_patient_recommendations(avg_compliance, recent_trends, health_metrics)
        
        return PatientAnalytics(
            patient_id=patient_id,
            total_diet_charts=total_charts,
            avg_compliance=avg_compliance,
            recent_trends=recent_trends,
            health_metrics=health_metrics,
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error("Get patient analytics failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get patient analytics")

@router.get("/compliance/{chart_id}", response_model=ComplianceMetrics)
async def get_compliance_metrics(
    chart_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed compliance metrics for a diet chart"""
    try:
        firebase_client = FirebaseClient()
        await firebase_client.initialize()
        
        # Get chart
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
        
        # Calculate compliance metrics
        meals = chart_data.get("meals", [])
        meal_compliance = {}
        nutrition_balance = {}
        
        for meal in meals:
            meal_type = meal.get("meal_type", "unknown")
            analysis = meal.get("analysis", {})
            
            # Calculate meal compliance
            meal_score = 0.5  # Base score
            if "compatibility_check" in analysis:
                compat_score = analysis["compatibility_check"].get("score", 0.5)
                meal_score = (meal_score + compat_score) / 2
            
            if "rasa_analysis" in analysis:
                rasa_score = analysis["rasa_analysis"].get("balance_score", 0.5)
                meal_score = (meal_score + rasa_score) / 2
            
            meal_compliance[meal_type] = meal_score
        
        # Calculate nutrition balance
        total_nutrition = chart_data.get("total_nutrition", {})
        nutrition_balance = _calculate_nutrition_balance(total_nutrition)
        
        # Calculate overall compliance
        overall_compliance = chart_data.get("ayurvedic_compliance", 0.5)
        
        # Calculate Ayurvedic adherence
        ayurvedic_adherence = _calculate_ayurvedic_adherence(meals)
        
        # Identify improvement areas
        improvement_areas = _identify_improvement_areas(meal_compliance, nutrition_balance, ayurvedic_adherence)
        
        return ComplianceMetrics(
            chart_id=chart_id,
            overall_compliance=overall_compliance,
            meal_compliance=meal_compliance,
            nutrition_balance=nutrition_balance,
            ayurvedic_adherence=ayurvedic_adherence,
            improvement_areas=improvement_areas
        )
        
    except Exception as e:
        logger.error("Get compliance metrics failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get compliance metrics")

@router.get("/dashboard")
async def get_dashboard_analytics(
    current_user: dict = Depends(get_current_user)
):
    """Get dashboard analytics for current user"""
    try:
        firebase_client = FirebaseClient()
        await firebase_client.initialize()
        
        user_role = current_user.get("role", "patient")
        uid = current_user.get("uid")
        
        if user_role == "patient":
            return await _get_patient_dashboard(firebase_client, uid)
        elif user_role == "doctor":
            return await _get_doctor_dashboard(firebase_client, uid)
        elif user_role == "admin":
            return await _get_admin_dashboard(firebase_client)
        else:
            raise HTTPException(status_code=403, detail="Invalid user role")
        
    except Exception as e:
        logger.error("Get dashboard analytics failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get dashboard analytics")

async def _get_patient_dashboard(firebase_client: FirebaseClient, patient_id: str) -> Dict[str, Any]:
    """Get patient dashboard data"""
    # Get recent diet charts
    charts_query = firebase_client.get_collection("diet_charts").where(
        "patient_id", "==", patient_id
    ).order_by("created_at", direction="DESCENDING").limit(5)
    
    recent_charts = list(charts_query.stream())
    
    # Calculate basic metrics
    total_charts = len(recent_charts)
    avg_compliance = 0.5
    if recent_charts:
        compliance_scores = [chart.to_dict().get("ayurvedic_compliance", 0.5) for chart in recent_charts]
        avg_compliance = sum(compliance_scores) / len(compliance_scores)
    
    return {
        "user_type": "patient",
        "total_diet_charts": total_charts,
        "avg_compliance": avg_compliance,
        "recent_charts": [chart.to_dict() for chart in recent_charts],
        "quick_stats": {
            "charts_this_month": total_charts,
            "compliance_trend": "improving" if avg_compliance > 0.6 else "needs_attention"
        }
    }

async def _get_doctor_dashboard(firebase_client: FirebaseClient, doctor_id: str) -> Dict[str, Any]:
    """Get doctor dashboard data"""
    # Get assigned patients
    patients_query = firebase_client.get_collection("patients").where(
        "assigned_doctor", "==", doctor_id
    )
    patients = list(patients_query.stream())
    
    # Get recent diet charts created by doctor
    charts_query = firebase_client.get_collection("diet_charts").where(
        "created_by", "==", doctor_id
    ).order_by("created_at", direction="DESCENDING").limit(10)
    
    recent_charts = list(charts_query.stream())
    
    # Calculate metrics
    total_patients = len(patients)
    total_charts = len(recent_charts)
    
    return {
        "user_type": "doctor",
        "total_patients": total_patients,
        "total_charts": total_charts,
        "recent_patients": [patient.to_dict() for patient in patients[:5]],
        "recent_charts": [chart.to_dict() for chart in recent_charts],
        "quick_stats": {
            "active_patients": total_patients,
            "charts_this_month": total_charts
        }
    }

async def _get_admin_dashboard(firebase_client: FirebaseClient) -> Dict[str, Any]:
    """Get admin dashboard data"""
    # Get all users
    users_query = firebase_client.get_collection("users")
    users = list(users_query.stream())
    
    # Get all patients
    patients_query = firebase_client.get_collection("patients")
    patients = list(patients_query.stream())
    
    # Get all diet charts
    charts_query = firebase_client.get_collection("diet_charts")
    charts = list(charts_query.stream())
    
    # Calculate metrics
    total_users = len(users)
    total_patients = len(patients)
    total_charts = len(charts)
    
    # Count by role
    role_counts = {}
    for user in users:
        role = user.to_dict().get("role", "unknown")
        role_counts[role] = role_counts.get(role, 0) + 1
    
    return {
        "user_type": "admin",
        "total_users": total_users,
        "total_patients": total_patients,
        "total_charts": total_charts,
        "role_distribution": role_counts,
        "quick_stats": {
            "active_users": total_users,
            "total_patients": total_patients,
            "charts_generated": total_charts
        }
    }

def _analyze_compliance_trends(charts: List) -> Dict[str, Any]:
    """Analyze compliance trends over time"""
    if not charts:
        return {"trend": "no_data", "direction": "stable"}
    
    # Sort charts by date
    sorted_charts = sorted(charts, key=lambda x: x.to_dict().get("created_at", ""))
    
    # Get compliance scores
    compliance_scores = [chart.to_dict().get("ayurvedic_compliance", 0.5) for chart in sorted_charts]
    
    if len(compliance_scores) < 2:
        return {"trend": "insufficient_data", "direction": "stable"}
    
    # Calculate trend
    recent_avg = sum(compliance_scores[-3:]) / min(3, len(compliance_scores))
    earlier_avg = sum(compliance_scores[:-3]) / max(1, len(compliance_scores) - 3) if len(compliance_scores) > 3 else recent_avg
    
    if recent_avg > earlier_avg + 0.1:
        direction = "improving"
    elif recent_avg < earlier_avg - 0.1:
        direction = "declining"
    else:
        direction = "stable"
    
    return {
        "trend": "analyzed",
        "direction": direction,
        "recent_avg": recent_avg,
        "earlier_avg": earlier_avg
    }

def _calculate_health_metrics(charts: List) -> Dict[str, Any]:
    """Calculate health-related metrics"""
    if not charts:
        return {"status": "no_data"}
    
    # Calculate average nutrition across all charts
    total_nutrition = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'fiber': 0}
    chart_count = 0
    
    for chart in charts:
        chart_data = chart.to_dict()
        nutrition = chart_data.get("total_nutrition", {})
        for nutrient, value in nutrition.items():
            if nutrient in total_nutrition:
                total_nutrition[nutrient] += value
        chart_count += 1
    
    if chart_count > 0:
        avg_nutrition = {nutrient: value / chart_count for nutrient, value in total_nutrition.items()}
    else:
        avg_nutrition = total_nutrition
    
    return {
        "avg_daily_nutrition": avg_nutrition,
        "nutrition_balance": _calculate_nutrition_balance(avg_nutrition),
        "status": "calculated"
    }

def _calculate_nutrition_balance(nutrition: Dict[str, float]) -> Dict[str, float]:
    """Calculate nutrition balance scores"""
    # Simplified balance calculation
    balance_scores = {}
    
    # Ideal ratios (simplified)
    ideal_ratios = {
        'protein': 0.15,  # 15% of calories
        'carbs': 0.55,    # 55% of calories
        'fat': 0.30       # 30% of calories
    }
    
    total_calories = nutrition.get('calories', 1)
    
    for nutrient, ideal_ratio in ideal_ratios.items():
        if nutrient in nutrition and total_calories > 0:
            actual_ratio = nutrition[nutrient] / total_calories
            balance_scores[nutrient] = min(actual_ratio / ideal_ratio, 1.0)
        else:
            balance_scores[nutrient] = 0.5
    
    return balance_scores

def _calculate_ayurvedic_adherence(meals: List[Dict]) -> float:
    """Calculate Ayurvedic adherence score"""
    if not meals:
        return 0.5
    
    adherence_scores = []
    
    for meal in meals:
        analysis = meal.get("analysis", {})
        meal_score = 0.5  # Base score
        
        # Check compatibility
        if "compatibility_check" in analysis:
            compat_score = analysis["compatibility_check"].get("score", 0.5)
            meal_score = (meal_score + compat_score) / 2
        
        # Check rasa balance
        if "rasa_analysis" in analysis:
            rasa_score = analysis["rasa_analysis"].get("balance_score", 0.5)
            meal_score = (meal_score + rasa_score) / 2
        
        adherence_scores.append(meal_score)
    
    return sum(adherence_scores) / len(adherence_scores)

def _identify_improvement_areas(meal_compliance: Dict, nutrition_balance: Dict, ayurvedic_adherence: float) -> List[str]:
    """Identify areas for improvement"""
    improvement_areas = []
    
    # Check meal compliance
    for meal_type, score in meal_compliance.items():
        if score < 0.6:
            improvement_areas.append(f"Improve {meal_type} compliance")
    
    # Check nutrition balance
    for nutrient, score in nutrition_balance.items():
        if score < 0.7:
            improvement_areas.append(f"Balance {nutrient} intake")
    
    # Check Ayurvedic adherence
    if ayurvedic_adherence < 0.6:
        improvement_areas.append("Improve Ayurvedic food combining")
    
    return improvement_areas

def _generate_patient_recommendations(avg_compliance: float, trends: Dict, health_metrics: Dict) -> List[str]:
    """Generate personalized recommendations"""
    recommendations = []
    
    if avg_compliance < 0.6:
        recommendations.append("Focus on following diet recommendations more closely")
    
    if trends.get("direction") == "declining":
        recommendations.append("Consider consulting with your doctor about recent changes")
    
    if health_metrics.get("nutrition_balance", {}).get("protein", 1.0) < 0.7:
        recommendations.append("Increase protein intake in your meals")
    
    if not recommendations:
        recommendations.append("Keep up the good work with your current diet plan")
    
    return recommendations
