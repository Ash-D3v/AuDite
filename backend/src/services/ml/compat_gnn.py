"""
Food Compatibility GNN Service
Integrates with the existing ayurvedic_compatibility_gnn.h5 model
"""

import tensorflow as tf
import numpy as np
import structlog
from typing import Dict, List, Any, Tuple
from functools import lru_cache
import os

logger = structlog.get_logger()

class CompatibilityGNN:
    """Food compatibility analysis using Graph Neural Network"""
    
    def __init__(self, model_path: str = "model/ayurvedic_compatibility_gnn.h5"):
        self.model_path = model_path
        self.model = None
        self.food_embeddings = None
        self.food_to_index = {}
        self._load_model()
    
    def _load_model(self):
        """Load the trained GNN model and food embeddings"""
        try:
            if not os.path.exists(self.model_path):
                logger.warning(f"Model file not found: {model_path}")
                return
            
            # Load the GNN model
            self.model = tf.keras.models.load_model(self.model_path)
            
            # Load food embeddings and mappings
            embeddings_path = "model/compatibility_encoders.pkl"
            if os.path.exists(embeddings_path):
                import pickle
                with open(embeddings_path, 'rb') as f:
                    data = pickle.load(f)
                    self.food_embeddings = data.get('embeddings')
                    self.food_to_index = data.get('food_to_index', {})
            
            logger.info("Compatibility GNN model loaded successfully")
            
        except Exception as e:
            logger.error("Failed to load compatibility GNN model", error=str(e))
            self.model = None
    
    @lru_cache(maxsize=256)
    def check_compatibility(self, food1: str, food2: str) -> Dict[str, Any]:
        """Check compatibility between two foods"""
        if self.model is None:
            logger.warning("Compatibility GNN model not available")
            return self._default_compatibility()
        
        try:
            # Get food indices
            idx1 = self.food_to_index.get(food1.lower())
            idx2 = self.food_to_index.get(food2.lower())
            
            if idx1 is None or idx2 is None:
                logger.warning(f"Food not found in embeddings: {food1}, {food2}")
                return self._default_compatibility()
            
            # Create adjacency matrix for the two foods
            num_foods = len(self.food_to_index)
            adj_matrix = np.zeros((num_foods, num_foods))
            adj_matrix[idx1, idx2] = 1
            adj_matrix[idx2, idx1] = 1
            
            # Get embeddings for both foods
            food1_embedding = self.food_embeddings[idx1]
            food2_embedding = self.food_embeddings[idx2]
            
            # Prepare input for GNN
            node_features = np.vstack([food1_embedding, food2_embedding])
            adj_matrix_subset = adj_matrix[:2, :2]
            
            # Make prediction
            prediction = self.model.predict([
                node_features.reshape(1, 2, -1),
                adj_matrix_subset.reshape(1, 2, 2)
            ])
            
            compatibility_score = float(prediction[0][0])
            is_compatible = compatibility_score > 0.5
            
            return {
                'compatible': is_compatible,
                'score': compatibility_score,
                'explanation': self._get_compatibility_explanation(food1, food2, compatibility_score),
                'recommendations': self._get_compatibility_recommendations(food1, food2, is_compatible)
            }
            
        except Exception as e:
            logger.error("Compatibility check failed", error=str(e))
            return self._default_compatibility()
    
    def check_meal_compatibility(self, foods: List[str]) -> Dict[str, Any]:
        """Check compatibility of multiple foods in a meal"""
        if len(foods) < 2:
            return {'compatible': True, 'score': 1.0, 'conflicts': []}
        
        conflicts = []
        total_score = 0
        comparisons = 0
        
        for i in range(len(foods)):
            for j in range(i + 1, len(foods)):
                result = self.check_compatibility(foods[i], foods[j])
                total_score += result['score']
                comparisons += 1
                
                if not result['compatible']:
                    conflicts.append({
                        'food1': foods[i],
                        'food2': foods[j],
                        'score': result['score'],
                        'explanation': result['explanation']
                    })
        
        avg_score = total_score / comparisons if comparisons > 0 else 1.0
        is_compatible = len(conflicts) == 0
        
        return {
            'compatible': is_compatible,
            'score': avg_score,
            'conflicts': conflicts,
            'recommendations': self._get_meal_recommendations(conflicts)
        }
    
    def _default_compatibility(self) -> Dict[str, Any]:
        """Return default compatibility when model is unavailable"""
        return {
            'compatible': True,
            'score': 0.7,
            'explanation': 'Compatibility analysis unavailable',
            'recommendations': {
                'note': 'Follow traditional Ayurvedic food combining principles',
                'general': 'Avoid mixing incompatible food groups'
            }
        }
    
    def _get_compatibility_explanation(self, food1: str, food2: str, score: float) -> str:
        """Get explanation for compatibility score"""
        if score > 0.8:
            return f"{food1} and {food2} are highly compatible and work well together"
        elif score > 0.6:
            return f"{food1} and {food2} are moderately compatible"
        elif score > 0.4:
            return f"{food1} and {food2} have some compatibility issues"
        else:
            return f"{food1} and {food2} are incompatible and should not be eaten together"
    
    def _get_compatibility_recommendations(self, food1: str, food2: str, compatible: bool) -> Dict[str, str]:
        """Get recommendations based on compatibility"""
        if compatible:
            return {
                'action': 'Safe to combine',
                'timing': 'Can be eaten together',
                'note': 'These foods complement each other well'
            }
        else:
            return {
                'action': 'Avoid combining',
                'timing': 'Eat at least 2-3 hours apart',
                'note': 'These foods may cause digestive issues when combined'
            }
    
    def _get_meal_recommendations(self, conflicts: List[Dict]) -> Dict[str, Any]:
        """Get recommendations for meal compatibility issues"""
        if not conflicts:
            return {
                'status': 'Good',
                'message': 'All foods in the meal are compatible'
            }
        
        return {
            'status': 'Issues found',
            'message': f'Found {len(conflicts)} compatibility conflicts',
            'suggestions': [
                f"Consider removing {conflict['food1']} or {conflict['food2']}"
                for conflict in conflicts[:3]  # Top 3 conflicts
            ]
        }
