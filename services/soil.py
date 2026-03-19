"""
Soil service to fetch soil data from static JSON database
"""
import json
import os
from typing import Dict, Optional


class SoilService:
    """
    Service class to manage soil data
    """
    
    def __init__(self):
        # Get the path to soil.json
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_path = os.path.join(current_dir, "..", "data", "soil.json")
        self.soil_data = self._load_soil_data()
    
    def _load_soil_data(self) -> Dict:
        """
        Load soil data from JSON file
        
        Returns:
            dict: Soil data for different locations
        
        Raises:
            Exception: If JSON file cannot be loaded
        """
        try:
            with open(self.data_path, 'r') as f:
                data = json.load(f)
                return data
        except FileNotFoundError:
            raise Exception(f"Soil data file not found at {self.data_path}")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON in soil data file: {str(e)}")
    
    def get_soil(self, location: str) -> Dict:
        """
        Get soil data for a specific location
        
        Args:
            location (str): Location name (city)
        
        Returns:
            dict: Soil data including type, pH, fertility, and nutrient levels
        """
        # Normalize location name (title case for consistency)
        location_normalized = location.strip().title()
        
        # Try to find exact match
        if location_normalized in self.soil_data["locations"]:
            soil_info = self.soil_data["locations"][location_normalized].copy()
            soil_info["location"] = location_normalized
            soil_info["data_source"] = "recorded"
            return soil_info
        
        # Try partial match (in case location is part of a larger string)
        for key in self.soil_data["locations"].keys():
            if location_normalized in key or key in location_normalized:
                soil_info = self.soil_data["locations"][key].copy()
                soil_info["location"] = key
                soil_info["data_source"] = "recorded"
                return soil_info
        
        # Return default data if no match found
        default_soil = self.soil_data["default"].copy()
        default_soil["location"] = location_normalized
        default_soil["data_source"] = "default"
        return default_soil
    
    def get_soil_quality_score(self, location: str) -> float:
        """
        Calculate soil quality score (0-100) based on various parameters
        
        Args:
            location (str): Location name
        
        Returns:
            float: Soil quality score
        """
        soil = self.get_soil(location)
        
        # Scoring logic
        fertility_scores = {"High": 40, "Medium": 25, "Low": 10}
        nutrient_scores = {"High": 10, "Medium": 5, "Low": 2}
        
        score = 0
        score += fertility_scores.get(soil["fertility"], 15)
        score += nutrient_scores.get(soil["nitrogen"], 5)
        score += nutrient_scores.get(soil["phosphorus"], 5)
        score += nutrient_scores.get(soil["potassium"], 5)
        
        # pH score (optimal range 6.5-7.5)
        ph = soil["pH"]
        if 6.5 <= ph <= 7.5:
            score += 20
        elif 6.0 <= ph <= 8.0:
            score += 15
        else:
            score += 5
        
        # Organic matter score
        om = soil["organic_matter"]
        if om >= 2.0:
            score += 15
        elif om >= 1.5:
            score += 10
        else:
            score += 5
        
        return min(score, 100)
    
    def get_soil_recommendations(self, location: str) -> Dict:
        """
        Get soil improvement recommendations
        
        Args:
            location (str): Location name
        
        Returns:
            dict: Recommendations for soil improvement
        """
        soil = self.get_soil(location)
        recommendations = {
            "amendments": [],
            "crops_suitable": [],
            "irrigation_needs": ""
        }
        
        # pH-based recommendations
        if soil["pH"] < 6.0:
            recommendations["amendments"].append("Add lime to increase pH")
        elif soil["pH"] > 8.0:
            recommendations["amendments"].append("Add sulfur or organic matter to decrease pH")
        
        # Nutrient recommendations
        if soil["nitrogen"] == "Low":
            recommendations["amendments"].append("Apply nitrogen-rich fertilizers (urea, ammonium)")
        if soil["phosphorus"] == "Low":
            recommendations["amendments"].append("Apply phosphate fertilizers (DAP)")
        if soil["potassium"] == "Low":
            recommendations["amendments"].append("Apply potassium fertilizers (MOP)")
        
        # Crop suitability based on soil type
        soil_crop_map = {
            "Alluvial": ["Rice", "Wheat", "Sugarcane", "Cotton"],
            "Black Soil": ["Cotton", "Wheat", "Jowar", "Linseed"],
            "Red Soil": ["Groundnut", "Millets", "Tobacco", "Cotton"],
            "Laterite": ["Cashew", "Tea", "Coffee", "Rubber"],
            "Arid Soil": ["Bajra", "Wheat", "Cotton", "Maize"],
            "Mixed": ["Wheat", "Rice", "Bajra", "Cotton"]
        }
        
        recommendations["crops_suitable"] = soil_crop_map.get(
            soil["soil_type"], 
            ["Wheat", "Rice", "Pulses"]
        )
        
        # Irrigation needs
        if soil["soil_type"] in ["Arid Soil", "Red Soil"]:
            recommendations["irrigation_needs"] = "High - requires regular irrigation"
        elif soil["soil_type"] in ["Alluvial", "Black Soil"]:
            recommendations["irrigation_needs"] = "Medium - moderate water retention"
        else:
            recommendations["irrigation_needs"] = "Variable - depends on crop"
        
        return recommendations


# Create a singleton instance
soil_service = SoilService()


# Convenience function for direct import
def get_soil(location: str) -> Dict:
    """
    Convenience function to fetch soil data
    
    Args:
        location (str): Location name
    
    Returns:
        dict: Soil data
    """
    return soil_service.get_soil(location)
