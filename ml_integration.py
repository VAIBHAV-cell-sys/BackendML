"""
ML Integration Module for Existing Backend
Integrates crop prediction ML model with FastAPI endpoints
"""

from fastapi import HTTPException
from typing import Dict, Optional
import os
from ml_crop_prediction import CropPredictionModel

class MLPredictionService:
    """
    Service to integrate ML predictions with existing backend
    """
    
    def __init__(self, model_path='models/crop_prediction_model.pkl'):
        self.model = CropPredictionModel()
        self.model_path = model_path
        self._load_or_train_model()
    
    def _load_or_train_model(self):
        """
        Load existing model or train new one if not found
        """
        if os.path.exists(self.model_path):
            print(f"📦 Loading existing ML model from {self.model_path}")
            self.model.load_model(self.model_path)
        else:
            print("🔄 No trained model found. Training new model...")
            self.model.train()
            self.model.save_model(self.model_path)
    
    def convert_soil_nutrients(self, nutrient_level: str) -> int:
        """
        Convert nutrient level string to numeric
        
        Args:
            nutrient_level (str): "Low", "Medium", or "High"
        
        Returns:
            int: 0, 1, or 2
        """
        mapping = {
            "Low": 0,
            "Medium": 1,
            "High": 2
        }
        return mapping.get(nutrient_level, 1)
    
    def get_season(self, month: int) -> int:
        """
        Determine season based on month
        
        Args:
            month (int): Month (1-12)
        
        Returns:
            int: 0=Kharif, 1=Rabi, 2=Zaid
        """
        if month in [6, 7, 8, 9, 10]:  # June to October
            return 0  # Kharif
        elif month in [11, 12, 1, 2, 3]:  # November to March
            return 1  # Rabi
        else:  # April, May
            return 2  # Zaid
    
    def prepare_ml_features(self, weather_data: Dict, soil_data: Dict, month: int) -> Dict:
        """
        Prepare features from weather and soil data for ML prediction
        
        Args:
            weather_data (dict): Weather information
            soil_data (dict): Soil information
            month (int): Current month
        
        Returns:
            dict: Features ready for ML model
        """
        features = {
            # Weather features
            'temperature': weather_data.get('temp', 25.0),
            'humidity': weather_data.get('humidity', 60.0),
            'rainfall': weather_data.get('rain', 0.0),
            'wind_speed': weather_data.get('wind_speed', 5.0),
            'pressure': weather_data.get('pressure', 1013.0),
            'cloud_cover': weather_data.get('clouds', 50.0),
            
            # Soil features
            'soil_pH': soil_data.get('pH', 7.0),
            'soil_nitrogen': self.convert_soil_nutrients(soil_data.get('nitrogen', 'Medium')),
            'soil_phosphorus': self.convert_soil_nutrients(soil_data.get('phosphorus', 'Medium')),
            'soil_potassium': self.convert_soil_nutrients(soil_data.get('potassium', 'Medium')),
            'soil_organic_matter': soil_data.get('organic_matter', 1.5),
            
            # Temporal features
            'season': self.get_season(month),
            'month': month
        }
        
        return features
    
    def get_ml_prediction(self, location: str, weather_data: Dict, 
                          soil_data: Dict, month: Optional[int] = None) -> Dict:
        """
        Get ML-based crop prediction
        
        Args:
            location (str): Location name
            weather_data (dict): Current weather data
            soil_data (dict): Soil data
            month (int, optional): Current month (defaults to current system month)
        
        Returns:
            dict: ML prediction results
        """
        from datetime import datetime
        
        if month is None:
            month = datetime.now().month
        
        try:
            # Prepare features
            ml_features = self.prepare_ml_features(weather_data, soil_data, month)
            
            # Get prediction
            prediction = self.model.predict(ml_features)
            
            # Add metadata
            prediction['location'] = location
            prediction['method'] = 'machine_learning'
            prediction['model_type'] = 'RandomForest'
            
            return prediction
        
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"ML prediction failed: {str(e)}"
            )
    
    def compare_predictions(self, rule_based_crop: str, ml_prediction: Dict) -> Dict:
        """
        Compare rule-based and ML predictions
        
        Args:
            rule_based_crop (str): Crop from rule-based engine
            ml_prediction (dict): ML prediction results
        
        Returns:
            dict: Comparison results
        """
        ml_crop = ml_prediction['primary_recommendation']
        
        # Check if rule-based matches ML top 3
        ml_top_crops = [rec['crop'] for rec in ml_prediction['all_recommendations']]
        
        agreement = rule_based_crop in ml_top_crops
        
        comparison = {
            'rule_based_recommendation': rule_based_crop,
            'ml_recommendation': ml_crop,
            'agreement': agreement,
            'ml_confidence': ml_prediction['confidence'],
            'ml_top_3': ml_top_crops
        }
        
        if agreement:
            comparison['verdict'] = 'Both methods agree - High confidence recommendation'
            if rule_based_crop == ml_crop:
                comparison['strength'] = 'Strong'
            else:
                comparison['strength'] = 'Moderate'
        else:
            comparison['verdict'] = 'Different recommendations - Consider both options'
            comparison['strength'] = 'Weak'
        
        return comparison


# Create singleton instance
ml_service = MLPredictionService()


# Convenience function for direct import
def get_ml_prediction(location: str, weather_data: Dict, 
                      soil_data: Dict, month: Optional[int] = None) -> Dict:
    """
    Convenience function to get ML prediction
    """
    return ml_service.get_ml_prediction(location, weather_data, soil_data, month)


def compare_with_rules(rule_based_crop: str, ml_prediction: Dict) -> Dict:
    """
    Convenience function to compare predictions
    """
    return ml_service.compare_predictions(rule_based_crop, ml_prediction)
