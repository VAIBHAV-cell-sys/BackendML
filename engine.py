"""
Core decision engine for crop recommendations
Analyzes weather, soil, and market data to provide actionable advice
"""
from typing import Dict, List, Tuple
from services.weather import get_weather
from services.soil import get_soil, soil_service
from services.mandi import get_price, mandi_service


class FarmAnalysisEngine:
    """
    Core engine that analyzes farm conditions and makes crop recommendations
    """
    
    def __init__(self):
        pass
    
    def analyze_farm(self, location: str) -> Dict:
        """
        Main analysis function that combines weather, soil, and market data
        to provide comprehensive farm analysis and crop recommendations
        
        Args:
            location (str): Location/city name
        
        Returns:
            dict: Complete analysis with recommended crop, reasoning, risk, and prices
        """
        try:
            # Step 1: Fetch all required data
            weather_data = get_weather(location)
            soil_data = get_soil(location)
            
            # Step 2: Apply decision logic to recommend crop
            crop_recommendation = self._decide_crop(weather_data, soil_data)
            
            # Step 3: Assess risk level
            risk_level = self._assess_risk(weather_data, soil_data, crop_recommendation["crop"])
            
            # Step 4: Get market price for recommended crop
            price_data = get_price(crop_recommendation["crop"])
            
            # Step 5: Get profit estimate
            profit_estimate = mandi_service.get_profit_estimate(crop_recommendation["crop"])
            
            # Step 6: Get alternative crops
            alternatives = self._get_alternative_crops(weather_data, soil_data)
            
            # Step 7: Compile complete analysis
            analysis = {
                "location": location,
                "recommended_crop": crop_recommendation["crop"],
                "reason": crop_recommendation["reason"],
                "confidence": crop_recommendation["confidence"],
                "risk_level": risk_level["level"],
                "risk_factors": risk_level["factors"],
                "weather": {
                    "temperature": weather_data["temp"],
                    "humidity": weather_data["humidity"],
                    "rainfall": weather_data["rain"],
                    "condition": weather_data["condition"],
                    "description": weather_data["description"]
                },
                "soil": {
                    "type": soil_data["soil_type"],
                    "pH": soil_data["pH"],
                    "fertility": soil_data["fertility"],
                    "nitrogen": soil_data["nitrogen"],
                    "phosphorus": soil_data["phosphorus"],
                    "potassium": soil_data["potassium"]
                },
                "market": {
                    "crop": price_data["crop"],
                    "price_per_quintal": price_data.get("current_price", price_data["price"]),
                    "trend": price_data["trend"],
                    "min_price": price_data["min_price"],
                    "max_price": price_data["max_price"]
                },
                "profit_estimate": profit_estimate,
                "alternative_crops": alternatives,
                "soil_quality_score": soil_service.get_soil_quality_score(location)
            }
            
            return analysis
        
        except Exception as e:
            raise Exception(f"Farm analysis failed: {str(e)}")
    
    def _decide_crop(self, weather: Dict, soil: Dict) -> Dict:
        """
        Core decision logic for crop recommendation based on weather and soil
        
        Args:
            weather (dict): Weather data
            soil (dict): Soil data
        
        Returns:
            dict: Recommended crop with reasoning and confidence
        """
        temp = weather["temp"]
        humidity = weather["humidity"]
        rainfall = weather["rain"]
        soil_type = soil["soil_type"]
        soil_pH = soil["pH"]
        fertility = soil["fertility"]
        
        # Decision tree based on multiple factors
        reasons = []
        crop = None
        confidence = 0
        
        # RULE 1: Low rainfall conditions (< 1mm)
        if rainfall < 1:
            if soil_type in ["Arid Soil", "Red Soil"]:
                crop = "Bajra"
                reasons.append("Low rainfall with arid/red soil is ideal for drought-resistant bajra")
                confidence = 85
            elif temp > 30:
                crop = "Cotton"
                reasons.append("Hot and dry conditions favor cotton cultivation")
                confidence = 75
            else:
                crop = "Wheat"
                reasons.append("Low rainfall with moderate temperature suits wheat")
                confidence = 70
        
        # RULE 2: Moderate rainfall (1-5mm)
        elif 1 <= rainfall < 5:
            if soil_type == "Black Soil":
                crop = "Cotton"
                reasons.append("Black soil with moderate rainfall is excellent for cotton")
                confidence = 90
            elif soil_type == "Alluvial":
                crop = "Wheat"
                reasons.append("Alluvial soil with moderate water availability is perfect for wheat")
                confidence = 85
            elif temp > 25:
                crop = "Maize"
                reasons.append("Warm temperature with moderate rain supports maize")
                confidence = 75
            else:
                crop = "Jowar"
                reasons.append("Moderate conditions are suitable for jowar")
                confidence = 70
        
        # RULE 3: High rainfall (>= 5mm)
        else:
            if soil_type in ["Alluvial", "Black Soil"]:
                crop = "Rice"
                reasons.append("High rainfall with water-retentive soil is ideal for rice")
                confidence = 90
            elif soil_type == "Laterite":
                crop = "Rice"
                reasons.append("Laterite soil with high rainfall can support rice cultivation")
                confidence = 75
            else:
                crop = "Sugarcane"
                reasons.append("High water availability supports sugarcane")
                confidence = 70
        
        # RULE 4: Soil fertility adjustments
        if fertility == "High":
            if crop in ["Wheat", "Rice"]:
                confidence += 10
                reasons.append("High soil fertility enhances yield potential")
        elif fertility == "Low":
            if crop not in ["Bajra", "Jowar"]:
                confidence -= 10
                reasons.append("Consider soil enrichment for optimal yields")
        
        # RULE 5: pH-based adjustments
        if 6.5 <= soil_pH <= 7.5:
            confidence += 5
            reasons.append("Optimal pH range for most crops")
        elif soil_pH < 6.0:
            if crop == "Rice":
                confidence += 5
                reasons.append("Slightly acidic soil is acceptable for rice")
        elif soil_pH > 8.0:
            if crop in ["Bajra", "Jowar"]:
                confidence += 5
                reasons.append("Alkaline soil is suitable for millets")
            else:
                reasons.append("Consider pH correction for better results")
        
        # RULE 6: Temperature-based fine-tuning
        if temp > 35:
            if crop not in ["Cotton", "Bajra", "Jowar"]:
                confidence -= 10
                reasons.append("High temperature may stress non-heat-tolerant crops")
        elif temp < 15:
            if crop not in ["Wheat", "Potato"]:
                confidence -= 10
                reasons.append("Low temperature may affect crop growth")
        
        # Cap confidence at 100
        confidence = min(confidence, 100)
        
        return {
            "crop": crop,
            "reason": " | ".join(reasons),
            "confidence": confidence
        }
    
    def _assess_risk(self, weather: Dict, soil: Dict, crop: str) -> Dict:
        """
        Assess cultivation risk based on current conditions
        
        Args:
            weather (dict): Weather data
            soil (dict): Soil data
            crop (str): Recommended crop
        
        Returns:
            dict: Risk level and contributing factors
        """
        risk_score = 0
        risk_factors = []
        
        # Weather-based risks
        if weather["temp"] > 38:
            risk_score += 25
            risk_factors.append("Extreme heat may cause crop stress")
        elif weather["temp"] < 10:
            risk_score += 25
            risk_factors.append("Cold temperature risk for most crops")
        
        if weather["humidity"] < 30:
            risk_score += 15
            risk_factors.append("Low humidity increases water stress")
        elif weather["humidity"] > 85:
            risk_score += 10
            risk_factors.append("High humidity may promote fungal diseases")
        
        # Soil-based risks
        if soil["fertility"] == "Low":
            risk_score += 20
            risk_factors.append("Low soil fertility requires additional inputs")
        
        if soil["pH"] < 5.5 or soil["pH"] > 8.5:
            risk_score += 15
            risk_factors.append("Soil pH outside optimal range")
        
        # Crop-specific risks
        water_intensive_crops = ["Rice", "Sugarcane"]
        if crop in water_intensive_crops and weather["rain"] < 2:
            risk_score += 20
            risk_factors.append(f"{crop} requires high water availability")
        
        # Determine risk level
        if risk_score <= 20:
            level = "Low"
        elif risk_score <= 40:
            level = "Medium"
        elif risk_score <= 60:
            level = "High"
        else:
            level = "Very High"
        
        if not risk_factors:
            risk_factors.append("Conditions are favorable for cultivation")
        
        return {
            "level": level,
            "score": risk_score,
            "factors": risk_factors
        }
    
    def _get_alternative_crops(self, weather: Dict, soil: Dict) -> List[Dict]:
        """
        Get alternative crop options based on conditions
        
        Args:
            weather (dict): Weather data
            soil (dict): Soil data
        
        Returns:
            list: List of alternative crops with suitability scores
        """
        # Get soil-suitable crops
        soil_recommendations = soil_service.get_soil_recommendations(soil["location"])
        suitable_crops = soil_recommendations.get("crops_suitable", [])
        
        alternatives = []
        
        for crop in suitable_crops[:3]:  # Top 3 alternatives
            # Calculate suitability score
            crop_analysis = self._decide_crop(weather, soil)
            price_data = get_price(crop)
            
            # Simple suitability calculation
            suitability = 60  # Base score
            
            if crop.lower() in soil["soil_type"].lower():
                suitability += 20
            
            if weather["rain"] > 3 and crop.lower() in ["rice", "sugarcane"]:
                suitability += 15
            elif weather["rain"] < 2 and crop.lower() in ["bajra", "jowar", "cotton"]:
                suitability += 15
            
            alternatives.append({
                "crop": crop,
                "suitability_score": min(suitability, 100),
                "price_per_quintal": price_data.get("current_price", price_data["price"]),
                "market_trend": price_data["trend"]
            })
        
        # Sort by suitability
        alternatives.sort(key=lambda x: x["suitability_score"], reverse=True)
        
        return alternatives


# Create singleton instance
farm_engine = FarmAnalysisEngine()


# Convenience function for direct import
def analyze_farm(location: str) -> Dict:
    """
    Convenience function to analyze farm conditions
    
    Args:
        location (str): Location name
    
    Returns:
        dict: Complete farm analysis
    """
    return farm_engine.analyze_farm(location)
