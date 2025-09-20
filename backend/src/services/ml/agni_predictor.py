"""
Agni Predictor Service - LSTM Time Series Model
Digestive power assessment using LSTM neural network
"""

import tensorflow as tf
import numpy as np
import structlog
from typing import Dict, List, Any, Optional, Tuple
from functools import lru_cache
import os
from datetime import datetime, timedelta

logger = structlog.get_logger()

class AgniPredictor:
    """Agni (Digestive Fire) Predictor using LSTM Time Series"""
    
    def __init__(self, model_path: str = "model/agni_predictor.h5"):
        self.model_path = model_path
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.sequence_length = 7  # 7 days of data for prediction
        self._load_model()
    
    def _load_model(self):
        """Load the trained LSTM model and scaler"""
        try:
            if not os.path.exists(self.model_path):
                logger.warning(f"Agni predictor model not found: {self.model_path}")
                return
            
            # Load the LSTM model
            self.model = tf.keras.models.load_model(self.model_path)
            
            # Load scaler and feature names (if available)
            scaler_path = "model/agni_scaler.pkl"
            if os.path.exists(scaler_path):
                import pickle
                with open(scaler_path, 'rb') as f:
                    scaler_data = pickle.load(f)
                    self.scaler = scaler_data.get('scaler')
                    self.feature_names = scaler_data.get('feature_names', [])
            else:
                # Default feature names for Agni prediction
                self.feature_names = [
                    'appetite_score', 'digestion_quality', 'bowel_movement_frequency',
                    'energy_level', 'sleep_quality', 'stress_level', 'meal_timing_consistency',
                    'water_intake', 'exercise_frequency', 'weather_impact'
                ]
            
            logger.info("Agni predictor LSTM model loaded successfully")
            
        except Exception as e:
            logger.error("Failed to load Agni predictor model", error=str(e))
            self.model = None
    
    def predict_agni_trend(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict Agni trend from historical data"""
        if self.model is None:
            logger.warning("Agni predictor model not available")
            return self._default_agni_prediction()
        
        try:
            # Prepare time series data
            features = self._prepare_time_series_data(historical_data)
            
            if features is None or len(features) < self.sequence_length:
                logger.warning("Insufficient historical data for prediction")
                return self._default_agni_prediction()
            
            # Reshape for LSTM input (samples, timesteps, features)
            X = features.reshape(1, self.sequence_length, -1)
            
            # Make prediction
            prediction = self.model.predict(X, verbose=0)
            
            # Interpret prediction
            agni_score = float(prediction[0][0])
            trend_direction = self._interpret_agni_trend(agni_score, historical_data)
            
            return {
                'agni_score': agni_score,
                'trend_direction': trend_direction,
                'confidence': self._calculate_confidence(features),
                'prediction_date': datetime.utcnow().isoformat(),
                'recommendations': self._get_agni_recommendations(agni_score, trend_direction),
                'next_week_forecast': self._generate_weekly_forecast(features)
            }
            
        except Exception as e:
            logger.error("Agni prediction failed", error=str(e))
            return self._default_agni_prediction()
    
    def assess_daily_agni(self, daily_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Assess daily Agni based on current metrics"""
        try:
            # Convert daily metrics to feature vector
            features = self._convert_daily_metrics_to_features(daily_metrics)
            
            if self.model is None:
                return self._assess_agni_without_model(features)
            
            # Use the last layer of LSTM for single-day assessment
            # This is a simplified approach - in practice, you might have a separate model
            agni_score = self._calculate_agni_score_from_features(features)
            
            return {
                'agni_score': agni_score,
                'agni_level': self._classify_agni_level(agni_score),
                'strength': self._assess_agni_strength(agni_score),
                'recommendations': self._get_daily_agni_recommendations(agni_score),
                'improvement_areas': self._identify_improvement_areas(features),
                'assessment_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Daily Agni assessment failed", error=str(e))
            return self._default_daily_agni_assessment()
    
    def predict_agni_impact_of_meal(self, meal_data: Dict[str, Any], current_agni: float) -> Dict[str, Any]:
        """Predict how a meal will impact current Agni"""
        try:
            # Extract meal features
            meal_features = self._extract_meal_features(meal_data)
            
            # Calculate impact based on meal properties and current Agni
            impact_score = self._calculate_meal_agni_impact(meal_features, current_agni)
            
            return {
                'impact_score': impact_score,
                'agni_change': self._predict_agni_change(impact_score, current_agni),
                'impact_level': self._classify_impact_level(impact_score),
                'recommendations': self._get_meal_agni_recommendations(impact_score, current_agni),
                'timing_advice': self._get_timing_advice(impact_score, current_agni)
            }
            
        except Exception as e:
            logger.error("Meal Agni impact prediction failed", error=str(e))
            return self._default_meal_impact_assessment()
    
    def _prepare_time_series_data(self, historical_data: List[Dict[str, Any]]) -> Optional[np.ndarray]:
        """Prepare time series data for LSTM input"""
        try:
            if len(historical_data) < self.sequence_length:
                return None
            
            # Take the most recent data points
            recent_data = historical_data[-self.sequence_length:]
            
            features = []
            for data_point in recent_data:
                feature_vector = self._convert_daily_metrics_to_features(data_point)
                features.append(feature_vector)
            
            return np.array(features)
            
        except Exception as e:
            logger.error("Time series data preparation failed", error=str(e))
            return None
    
    def _convert_daily_metrics_to_features(self, daily_metrics: Dict[str, Any]) -> np.ndarray:
        """Convert daily metrics to feature vector"""
        try:
            # Map metrics to numerical values
            feature_mapping = {
                'appetite_score': lambda x: min(max(x, 0), 10) / 10.0,  # 0-1 scale
                'digestion_quality': lambda x: min(max(x, 0), 10) / 10.0,
                'bowel_movement_frequency': lambda x: min(max(x, 0), 3) / 3.0,  # 0-3 times per day
                'energy_level': lambda x: min(max(x, 0), 10) / 10.0,
                'sleep_quality': lambda x: min(max(x, 0), 10) / 10.0,
                'stress_level': lambda x: min(max(x, 0), 10) / 10.0,
                'meal_timing_consistency': lambda x: 1.0 if x else 0.0,
                'water_intake': lambda x: min(max(x, 0), 3) / 3.0,  # 0-3 liters
                'exercise_frequency': lambda x: min(max(x, 0), 7) / 7.0,  # 0-7 times per week
                'weather_impact': lambda x: min(max(x, -5), 5) / 5.0 + 0.5  # -5 to 5, normalized to 0-1
            }
            
            features = []
            for feature_name in self.feature_names:
                if feature_name in daily_metrics:
                    try:
                        value = feature_mapping[feature_name](daily_metrics[feature_name])
                        features.append(value)
                    except (KeyError, TypeError):
                        features.append(0.5)  # Default neutral value
                else:
                    features.append(0.5)  # Default neutral value
            
            return np.array(features)
            
        except Exception as e:
            logger.error("Feature conversion failed", error=str(e))
            return np.array([0.5] * len(self.feature_names))
    
    def _interpret_agni_trend(self, agni_score: float, historical_data: List[Dict[str, Any]]) -> str:
        """Interpret Agni trend direction"""
        if len(historical_data) < 2:
            return "stable"
        
        # Calculate recent average
        recent_scores = [self._calculate_agni_score_from_features(
            self._convert_daily_metrics_to_features(data)
        ) for data in historical_data[-3:]]
        
        recent_avg = np.mean(recent_scores)
        
        if agni_score > recent_avg + 0.1:
            return "improving"
        elif agni_score < recent_avg - 0.1:
            return "declining"
        else:
            return "stable"
    
    def _calculate_confidence(self, features: np.ndarray) -> float:
        """Calculate prediction confidence based on data quality"""
        try:
            # Confidence based on data completeness and consistency
            completeness = np.sum(features != 0.5) / len(features)  # 0.5 is default value
            consistency = 1.0 - np.std(features)  # Lower std = higher consistency
            
            confidence = (completeness + consistency) / 2.0
            return min(max(confidence, 0.0), 1.0)
            
        except Exception as e:
            logger.error("Confidence calculation failed", error=str(e))
            return 0.5
    
    def _generate_weekly_forecast(self, features: np.ndarray) -> List[Dict[str, Any]]:
        """Generate 7-day Agni forecast"""
        try:
            forecast = []
            current_features = features[-1].copy()  # Start with most recent data
            
            for day in range(7):
                # Simple trend-based forecast (in practice, use the LSTM model)
                trend_factor = 0.95 + (day * 0.01)  # Slight upward trend
                predicted_score = self._calculate_agni_score_from_features(current_features) * trend_factor
                
                forecast.append({
                    'day': day + 1,
                    'agni_score': float(predicted_score),
                    'agni_level': self._classify_agni_level(predicted_score),
                    'confidence': max(0.5, 1.0 - (day * 0.1))  # Decreasing confidence
                })
                
                # Update features for next day (simplified)
                current_features = current_features * 0.95  # Slight decay
            
            return forecast
            
        except Exception as e:
            logger.error("Weekly forecast generation failed", error=str(e))
            return []
    
    def _calculate_agni_score_from_features(self, features: np.ndarray) -> float:
        """Calculate Agni score from feature vector"""
        try:
            if self.model is None:
                # Simple weighted average when model is not available
                weights = np.array([0.2, 0.2, 0.15, 0.15, 0.1, 0.1, 0.05, 0.03, 0.01, 0.01])
                return float(np.dot(features, weights))
            
            # Use model for prediction
            X = features.reshape(1, 1, -1)  # Single timestep
            prediction = self.model.predict(X, verbose=0)
            return float(prediction[0][0])
            
        except Exception as e:
            logger.error("Agni score calculation failed", error=str(e))
            return 0.5
    
    def _classify_agni_level(self, agni_score: float) -> str:
        """Classify Agni level based on score"""
        if agni_score >= 0.8:
            return "excellent"
        elif agni_score >= 0.6:
            return "good"
        elif agni_score >= 0.4:
            return "moderate"
        elif agni_score >= 0.2:
            return "poor"
        else:
            return "very_poor"
    
    def _assess_agni_strength(self, agni_score: float) -> str:
        """Assess Agni strength"""
        if agni_score >= 0.7:
            return "strong"
        elif agni_score >= 0.4:
            return "moderate"
        else:
            return "weak"
    
    def _get_agni_recommendations(self, agni_score: float, trend_direction: str) -> List[str]:
        """Get recommendations based on Agni score and trend"""
        recommendations = []
        
        if agni_score < 0.4:
            recommendations.extend([
                "Focus on improving digestive fire with warming foods",
                "Include ginger, black pepper, and cumin in your diet",
                "Eat at regular times to strengthen Agni",
                "Avoid cold and heavy foods"
            ])
        elif agni_score < 0.6:
            recommendations.extend([
                "Maintain current good practices",
                "Consider adding more digestive spices",
                "Ensure regular meal timing"
            ])
        else:
            recommendations.extend([
                "Excellent Agni! Maintain current practices",
                "Continue with balanced diet and regular routine"
            ])
        
        if trend_direction == "declining":
            recommendations.append("Agni is declining - focus on digestive health")
        elif trend_direction == "improving":
            recommendations.append("Great! Agni is improving - keep it up")
        
        return recommendations
    
    def _get_daily_agni_recommendations(self, agni_score: float) -> List[str]:
        """Get daily Agni recommendations"""
        if agni_score < 0.4:
            return [
                "Start the day with warm water and ginger",
                "Eat light, easily digestible foods",
                "Include digestive spices in every meal",
                "Avoid cold drinks and raw foods"
            ]
        elif agni_score < 0.6:
            return [
                "Maintain regular meal times",
                "Include some warming spices",
                "Stay hydrated with warm water"
            ]
        else:
            return [
                "Your Agni is strong today!",
                "Continue with your current routine",
                "Consider trying new healthy foods"
            ]
    
    def _identify_improvement_areas(self, features: np.ndarray) -> List[str]:
        """Identify areas for Agni improvement"""
        improvement_areas = []
        
        feature_importance = {
            'appetite_score': 'Appetite regulation',
            'digestion_quality': 'Digestive health',
            'bowel_movement_frequency': 'Bowel regularity',
            'energy_level': 'Energy management',
            'sleep_quality': 'Sleep hygiene',
            'stress_level': 'Stress management',
            'meal_timing_consistency': 'Meal timing',
            'water_intake': 'Hydration',
            'exercise_frequency': 'Physical activity',
            'weather_impact': 'Environmental adaptation'
        }
        
        for i, (feature_name, description) in enumerate(feature_importance.items()):
            if i < len(features) and features[i] < 0.4:
                improvement_areas.append(description)
        
        return improvement_areas
    
    def _extract_meal_features(self, meal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from meal data"""
        return {
            'food_heating_properties': meal_data.get('heating_properties', 0.5),
            'food_digestibility': meal_data.get('digestibility', 0.5),
            'meal_size': meal_data.get('meal_size', 0.5),
            'meal_timing': meal_data.get('meal_timing', 0.5),
            'spice_level': meal_data.get('spice_level', 0.5)
        }
    
    def _calculate_meal_agni_impact(self, meal_features: Dict[str, Any], current_agni: float) -> float:
        """Calculate meal impact on Agni"""
        try:
            # Weighted calculation based on meal properties
            weights = {
                'food_heating_properties': 0.3,
                'food_digestibility': 0.25,
                'meal_size': 0.2,
                'meal_timing': 0.15,
                'spice_level': 0.1
            }
            
            impact = sum(meal_features.get(key, 0.5) * weight for key, weight in weights.items())
            
            # Adjust based on current Agni level
            if current_agni < 0.4:  # Weak Agni
                impact *= 1.2  # Meals have more impact
            elif current_agni > 0.8:  # Strong Agni
                impact *= 0.8  # Meals have less impact
            
            return min(max(impact, 0.0), 1.0)
            
        except Exception as e:
            logger.error("Meal impact calculation failed", error=str(e))
            return 0.5
    
    def _predict_agni_change(self, impact_score: float, current_agni: float) -> float:
        """Predict how Agni will change after meal"""
        # Simple linear relationship
        change = (impact_score - 0.5) * 0.2  # Max change of ±0.1
        new_agni = current_agni + change
        return min(max(new_agni, 0.0), 1.0)
    
    def _classify_impact_level(self, impact_score: float) -> str:
        """Classify meal impact level"""
        if impact_score >= 0.7:
            return "high_positive"
        elif impact_score >= 0.6:
            return "positive"
        elif impact_score >= 0.4:
            return "neutral"
        elif impact_score >= 0.3:
            return "negative"
        else:
            return "high_negative"
    
    def _get_meal_agni_recommendations(self, impact_score: float, current_agni: float) -> List[str]:
        """Get meal-specific Agni recommendations"""
        if impact_score >= 0.6:
            return ["This meal will strengthen your Agni", "Good choice for digestive health"]
        elif impact_score >= 0.4:
            return ["This meal is neutral for Agni", "Consider adding digestive spices"]
        else:
            return ["This meal may weaken Agni", "Consider lighter alternatives", "Add warming spices"]
    
    def _get_timing_advice(self, impact_score: float, current_agni: float) -> str:
        """Get timing advice for meal"""
        if current_agni < 0.4:
            return "Eat when you feel hungry, avoid overeating"
        elif impact_score < 0.4:
            return "Eat smaller portions and wait 2-3 hours before next meal"
        else:
            return "Good timing for this meal"
    
    def _default_agni_prediction(self) -> Dict[str, Any]:
        """Return default Agni prediction when model is unavailable"""
        return {
            'agni_score': 0.5,
            'trend_direction': 'stable',
            'confidence': 0.3,
            'prediction_date': datetime.utcnow().isoformat(),
            'recommendations': ['Follow traditional Ayurvedic principles', 'Maintain regular routine'],
            'next_week_forecast': []
        }
    
    def _assess_agni_without_model(self, features: np.ndarray) -> Dict[str, Any]:
        """Assess Agni without ML model"""
        agni_score = self._calculate_agni_score_from_features(features)
        return {
            'agni_score': agni_score,
            'agni_level': self._classify_agni_level(agni_score),
            'strength': self._assess_agni_strength(agni_score),
            'recommendations': self._get_daily_agni_recommendations(agni_score),
            'improvement_areas': self._identify_improvement_areas(features),
            'assessment_date': datetime.utcnow().isoformat()
        }
    
    def _default_daily_agni_assessment(self) -> Dict[str, Any]:
        """Return default daily Agni assessment"""
        return {
            'agni_score': 0.5,
            'agni_level': 'moderate',
            'strength': 'moderate',
            'recommendations': ['Follow balanced approach', 'Listen to your body'],
            'improvement_areas': ['General wellness'],
            'assessment_date': datetime.utcnow().isoformat()
        }
    
    def _default_meal_impact_assessment(self) -> Dict[str, Any]:
        """Return default meal impact assessment"""
        return {
            'impact_score': 0.5,
            'agni_change': 0.0,
            'impact_level': 'neutral',
            'recommendations': ['Follow traditional food combining principles'],
            'timing_advice': 'Eat when hungry, stop when satisfied'
        }
