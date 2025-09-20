"""
Reports Router
"""

from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import structlog
import tempfile
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
from src.middleware.firebase_auth import get_current_user, get_current_uid, require_role
from src.services.firebase_client import FirebaseClient

logger = structlog.get_logger()
router = APIRouter()

# Pydantic models
class ReportRequest(BaseModel):
    chart_id: str
    include_analysis: bool = True
    include_nutrition: bool = True
    include_recommendations: bool = True

class ReportResponse(BaseModel):
    report_id: str
    chart_id: str
    generated_at: str
    download_url: str

@router.get("/diet-chart/{chart_id}/pdf")
async def generate_diet_chart_pdf(
    chart_id: str,
    include_analysis: bool = True,
    include_nutrition: bool = True,
    include_recommendations: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """Generate PDF report for diet chart"""
    try:
        firebase_client = FirebaseClient()
        await firebase_client.initialize()
        
        # Get chart data
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
        
        # Get patient data
        patient_doc = firebase_client.get_document("patients", chart_data.get("patient_id")).get()
        patient_data = patient_doc.to_dict() if patient_doc.exists else {}
        
        # Generate PDF
        pdf_file = _generate_diet_chart_pdf(
            chart_data, 
            patient_data, 
            include_analysis, 
            include_nutrition, 
            include_recommendations
        )
        
        # Return file response
        return FileResponse(
            pdf_file,
            media_type='application/pdf',
            filename=f"diet_chart_{chart_id}.pdf"
        )
        
    except Exception as e:
        logger.error("Generate diet chart PDF failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate PDF")

@router.post("/generate", response_model=ReportResponse)
async def generate_custom_report(
    report_request: ReportRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate custom report"""
    try:
        firebase_client = FirebaseClient()
        await firebase_client.initialize()
        
        # Get chart data
        chart_doc = firebase_client.get_document("diet_charts", report_request.chart_id).get()
        if not chart_doc.exists:
            raise HTTPException(status_code=404, detail="Diet chart not found")
        
        chart_data = chart_doc.to_dict()
        
        # Check permissions
        user_role = current_user.get("role", "patient")
        if user_role == "patient" and chart_data.get("patient_id") != current_user.get("uid"):
            raise HTTPException(status_code=403, detail="Access denied")
        elif user_role == "doctor" and chart_data.get("created_by") != current_user.get("uid"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Generate report
        report_id = f"report_{chart_id}_{int(datetime.utcnow().timestamp())}"
        pdf_file = _generate_diet_chart_pdf(
            chart_data,
            {},
            report_request.include_analysis,
            report_request.include_nutrition,
            report_request.include_recommendations
        )
        
        # Store report metadata
        report_doc = {
            "report_id": report_id,
            "chart_id": report_request.chart_id,
            "generated_by": current_user.get("uid"),
            "generated_at": firebase_client.db.SERVER_TIMESTAMP,
            "include_analysis": report_request.include_analysis,
            "include_nutrition": report_request.include_nutrition,
            "include_recommendations": report_request.include_recommendations
        }
        
        firebase_client.get_collection("reports").document(report_id).set(report_doc)
        
        return ReportResponse(
            report_id=report_id,
            chart_id=report_request.chart_id,
            generated_at=str(report_doc["generated_at"]),
            download_url=f"/reports/download/{report_id}"
        )
        
    except Exception as e:
        logger.error("Generate custom report failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate report")

@router.get("/download/{report_id}")
async def download_report(
    report_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Download generated report"""
    try:
        firebase_client = FirebaseClient()
        await firebase_client.initialize()
        
        # Get report data
        report_doc = firebase_client.get_document("reports", report_id).get()
        if not report_doc.exists:
            raise HTTPException(status_code=404, detail="Report not found")
        
        report_data = report_doc.to_dict()
        
        # Check permissions
        user_role = current_user.get("role", "patient")
        if user_role == "patient" and report_data.get("generated_by") != current_user.get("uid"):
            raise HTTPException(status_code=403, detail="Access denied")
        elif user_role == "doctor" and report_data.get("generated_by") != current_user.get("uid"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get chart data
        chart_doc = firebase_client.get_document("diet_charts", report_data.get("chart_id")).get()
        chart_data = chart_doc.to_dict() if chart_doc.exists else {}
        
        # Generate PDF
        pdf_file = _generate_diet_chart_pdf(
            chart_data,
            {},
            report_data.get("include_analysis", True),
            report_data.get("include_nutrition", True),
            report_data.get("include_recommendations", True)
        )
        
        return FileResponse(
            pdf_file,
            media_type='application/pdf',
            filename=f"report_{report_id}.pdf"
        )
        
    except Exception as e:
        logger.error("Download report failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to download report")

def _generate_diet_chart_pdf(
    chart_data: Dict[str, Any], 
    patient_data: Dict[str, Any],
    include_analysis: bool,
    include_nutrition: bool,
    include_recommendations: bool
) -> str:
    """Generate PDF for diet chart"""
    try:
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_file.close()
        
        # Create PDF document
        doc = SimpleDocTemplate(temp_file.name, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1,  # Center alignment
            textColor=colors.darkblue
        )
        
        story.append(Paragraph("Ayurvedic Diet Chart", title_style))
        story.append(Spacer(1, 20))
        
        # Patient Information
        if patient_data:
            patient_info = f"""
            <b>Patient:</b> {patient_data.get('full_name', 'N/A')}<br/>
            <b>Age:</b> {patient_data.get('age', 'N/A')}<br/>
            <b>Gender:</b> {patient_data.get('gender', 'N/A')}<br/>
            <b>Chart Duration:</b> {chart_data.get('duration_days', 7)} days
            """
            story.append(Paragraph(patient_info, styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Diet Chart Table
        meals = chart_data.get('meals', [])
        if meals:
            story.append(Paragraph("<b>Diet Plan</b>", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            for i, meal in enumerate(meals, 1):
                meal_type = meal.get('meal_type', f'Meal {i}').title()
                foods = meal.get('foods', [])
                
                # Meal header
                story.append(Paragraph(f"<b>{meal_type}</b>", styles['Heading3']))
                
                if foods:
                    # Create food table
                    food_data = [['Food Item', 'Quantity', 'Unit']]
                    for food in foods:
                        food_data.append([
                            food.get('name', ''),
                            str(food.get('quantity', 0)),
                            food.get('unit', 'grams')
                        ])
                    
                    food_table = Table(food_data)
                    food_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 12),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    
                    story.append(food_table)
                    story.append(Spacer(1, 12))
                
                # Include analysis if requested
                if include_analysis and 'analysis' in meal:
                    analysis = meal['analysis']
                    
                    # Compatibility check
                    if 'compatibility_check' in analysis:
                        compat = analysis['compatibility_check']
                        compat_text = f"<b>Compatibility:</b> {'✓ Compatible' if compat.get('compatible', False) else '✗ Incompatible'}"
                        if 'score' in compat:
                            compat_text += f" (Score: {compat['score']:.2f})"
                        story.append(Paragraph(compat_text, styles['Normal']))
                    
                    # Rasa analysis
                    if 'rasa_analysis' in analysis:
                        rasa = analysis['rasa_analysis']
                        if 'balance_score' in rasa:
                            story.append(Paragraph(f"<b>Rasa Balance:</b> {rasa['balance_score']:.2f}", styles['Normal']))
                
                story.append(Spacer(1, 20))
        
        # Nutrition Summary
        if include_nutrition and 'total_nutrition' in chart_data:
            nutrition = chart_data['total_nutrition']
            story.append(Paragraph("<b>Nutrition Summary</b>", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            nutrition_data = [
                ['Nutrient', 'Amount'],
                ['Calories', f"{nutrition.get('calories', 0):.1f} kcal"],
                ['Protein', f"{nutrition.get('protein', 0):.1f} g"],
                ['Carbohydrates', f"{nutrition.get('carbs', 0):.1f} g"],
                ['Fat', f"{nutrition.get('fat', 0):.1f} g"],
                ['Fiber', f"{nutrition.get('fiber', 0):.1f} g"]
            ]
            
            nutrition_table = Table(nutrition_data)
            nutrition_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(nutrition_table)
            story.append(Spacer(1, 20))
        
        # Ayurvedic Compliance
        compliance = chart_data.get('ayurvedic_compliance', 0.5)
        story.append(Paragraph(f"<b>Ayurvedic Compliance Score:</b> {compliance:.2f}", styles['Heading3']))
        story.append(Spacer(1, 20))
        
        # Recommendations
        if include_recommendations:
            story.append(Paragraph("<b>Recommendations</b>", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            recommendations = [
                "Follow the meal timings as suggested",
                "Ensure proper food combining principles",
                "Listen to your body's hunger and satiety signals",
                "Maintain regular eating schedule",
                "Stay hydrated throughout the day"
            ]
            
            for i, rec in enumerate(recommendations, 1):
                story.append(Paragraph(f"{i}. {rec}", styles['Normal']))
            
            story.append(Spacer(1, 20))
        
        # Footer
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Paragraph("Ayurvedic Diet Management System", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        return temp_file.name
        
    except Exception as e:
        logger.error("PDF generation failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate PDF")
