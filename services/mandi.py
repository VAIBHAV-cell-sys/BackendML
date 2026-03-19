"""
Mandi (Market) service to fetch crop prices
Uses mock data for demonstration purposes
"""
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import random


class MandiService:
    """
    Service class to manage market price data for crops
    """
    
    def __init__(self):
        # Mock price database (prices in INR per quintal)
        # In production, this would fetch from a real API or database
        self.base_prices = {
            "wheat": {
                "price": 2125,
                "unit": "quintal",
                "trend": "stable",
                "min_price": 2050,
                "max_price": 2200
            },
            "rice": {
                "price": 2800,
                "unit": "quintal",
                "trend": "rising",
                "min_price": 2700,
                "max_price": 2950
            },
            "bajra": {
                "price": 1950,
                "unit": "quintal",
                "trend": "stable",
                "min_price": 1850,
                "max_price": 2050
            },
            "maize": {
                "price": 1875,
                "unit": "quintal",
                "trend": "falling",
                "min_price": 1800,
                "max_price": 1950
            },
            "cotton": {
                "price": 6500,
                "unit": "quintal",
                "trend": "rising",
                "min_price": 6200,
                "max_price": 6800
            },
            "sugarcane": {
                "price": 315,
                "unit": "quintal",
                "trend": "stable",
                "min_price": 300,
                "max_price": 330
            },
            "groundnut": {
                "price": 5800,
                "unit": "quintal",
                "trend": "rising",
                "min_price": 5500,
                "max_price": 6100
            },
            "soybean": {
                "price": 4250,
                "unit": "quintal",
                "trend": "stable",
                "min_price": 4100,
                "max_price": 4400
            },
            "jowar": {
                "price": 3100,
                "unit": "quintal",
                "trend": "stable",
                "min_price": 2950,
                "max_price": 3250
            },
            "pulses": {
                "price": 6200,
                "unit": "quintal",
                "trend": "rising",
                "min_price": 5900,
                "max_price": 6500
            },
            "potato": {
                "price": 1200,
                "unit": "quintal",
                "trend": "falling",
                "min_price": 1000,
                "max_price": 1400
            },
            "onion": {
                "price": 1800,
                "unit": "quintal",
                "trend": "stable",
                "min_price": 1500,
                "max_price": 2100
            },
            "tomato": {
                "price": 2500,
                "unit": "quintal",
                "trend": "rising",
                "min_price": 2000,
                "max_price": 3000
            }
        }
        
        # Add slight random variation to simulate market fluctuation
        self._add_market_variation()
    
    def _add_market_variation(self):
        """
        Add realistic daily variation to prices (±2-5%)
        """
        for crop in self.base_prices:
            variation = random.uniform(-0.05, 0.05)  # ±5% variation
            base_price = self.base_prices[crop]["price"]
            self.base_prices[crop]["current_price"] = round(
                base_price * (1 + variation), 2
            )
    
    def get_price(self, crop: str) -> Dict:
        """
        Get current market price for a crop
        
        Args:
            crop (str): Crop name
        
        Returns:
            dict: Price information including current price, trend, and range
        """
        # Normalize crop name
        crop_normalized = crop.lower().strip()
        
        if crop_normalized in self.base_prices:
            price_data = self.base_prices[crop_normalized].copy()
            price_data["crop"] = crop.title()
            price_data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return price_data
        
        # Return default data if crop not found
        return {
            "crop": crop.title(),
            "price": 0,
            "current_price": 0,
            "unit": "quintal",
            "trend": "unknown",
            "min_price": 0,
            "max_price": 0,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error": "Price data not available for this crop"
        }
    
    def get_multiple_prices(self, crops: List[str]) -> Dict[str, Dict]:
        """
        Get prices for multiple crops at once
        
        Args:
            crops (list): List of crop names
        
        Returns:
            dict: Dictionary mapping crop names to their price data
        """
        return {crop: self.get_price(crop) for crop in crops}
    
    def get_profit_estimate(self, crop: str, area_acres: float = 1.0) -> Dict:
        """
        Calculate estimated profit for a crop based on typical yields
        
        Args:
            crop (str): Crop name
            area_acres (float): Cultivation area in acres (default 1 acre)
        
        Returns:
            dict: Profit estimation including revenue, costs, and profit
        """
        # Typical yields per acre (in quintals)
        typical_yields = {
            "wheat": 20,
            "rice": 25,
            "bajra": 18,
            "maize": 22,
            "cotton": 12,
            "sugarcane": 350,
            "groundnut": 15,
            "soybean": 12,
            "jowar": 16,
            "pulses": 10,
            "potato": 80,
            "onion": 100,
            "tomato": 150
        }
        
        # Typical cultivation costs per acre (in INR)
        cultivation_costs = {
            "wheat": 18000,
            "rice": 22000,
            "bajra": 15000,
            "maize": 16000,
            "cotton": 25000,
            "sugarcane": 45000,
            "groundnut": 20000,
            "soybean": 18000,
            "jowar": 14000,
            "pulses": 16000,
            "potato": 35000,
            "onion": 30000,
            "tomato": 40000
        }
        
        crop_normalized = crop.lower().strip()
        price_data = self.get_price(crop)
        
        if crop_normalized not in typical_yields:
            return {
                "error": "Profit estimation not available for this crop"
            }
        
        # Calculate revenue and profit
        yield_per_acre = typical_yields[crop_normalized]
        total_yield = yield_per_acre * area_acres
        price_per_quintal = price_data.get("current_price", price_data["price"])
        
        revenue = total_yield * price_per_quintal
        cost = cultivation_costs.get(crop_normalized, 20000) * area_acres
        profit = revenue - cost
        profit_margin = (profit / revenue * 100) if revenue > 0 else 0
        
        return {
            "crop": crop.title(),
            "area_acres": area_acres,
            "expected_yield_quintals": total_yield,
            "price_per_quintal": price_per_quintal,
            "total_revenue": round(revenue, 2),
            "cultivation_cost": round(cost, 2),
            "net_profit": round(profit, 2),
            "profit_margin_percent": round(profit_margin, 2),
            "roi_percent": round((profit / cost * 100) if cost > 0 else 0, 2)
        }
    
    def get_all_crops(self) -> List[str]:
        """
        Get list of all available crops
        
        Returns:
            list: List of crop names
        """
        return [crop.title() for crop in self.base_prices.keys()]
    
    def compare_crops(self, crops: List[str], area_acres: float = 1.0) -> List[Dict]:
        """
        Compare profit potential of multiple crops
        
        Args:
            crops (list): List of crop names to compare
            area_acres (float): Cultivation area in acres
        
        Returns:
            list: List of crop comparisons sorted by profit
        """
        comparisons = []
        
        for crop in crops:
            profit_data = self.get_profit_estimate(crop, area_acres)
            if "error" not in profit_data:
                comparisons.append(profit_data)
        
        # Sort by net profit (descending)
        comparisons.sort(key=lambda x: x["net_profit"], reverse=True)
        
        return comparisons


# Create a singleton instance
mandi_service = MandiService()


# Convenience function for direct import
def get_price(crop: str) -> Dict:
    """
    Convenience function to fetch crop price
    
    Args:
        crop (str): Crop name
    
    Returns:
        dict: Price data
    """
    return mandi_service.get_price(crop)
