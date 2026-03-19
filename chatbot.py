"""
Chatbot service integrating OpenAI API with farm analysis engine
Generates contextual, data-driven responses for farmers
"""
import json
from typing import Dict
from openai import OpenAI
from config import Config
from engine import analyze_farm


class AgriculturalChatbot:
    """
    AI-powered agricultural advisory chatbot
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL
        
        # System prompt that guides the AI's behavior
        self.system_prompt = """You are an AI agriculture advisor for Indian farmers. You must give clear, practical, and profit-oriented advice.

Your responsibilities:
1. Provide actionable farming advice based on current weather, soil, and market data
2. Consider the farmer's economic interests and suggest profitable crops
3. Warn about risks and provide mitigation strategies
4. Use simple, farmer-friendly language (avoid technical jargon when possible)
5. Always base your recommendations on the provided data

Response format requirements:
You MUST return your response strictly in JSON format with the following structure:
{
    "recommended_crop": "Name of the primary recommended crop",
    "reason": "Clear explanation of why this crop is recommended based on data",
    "risk_level": "Low/Medium/High/Very High",
    "profit_insight": "Financial analysis and profit potential",
    "action_steps": ["Step 1", "Step 2", "Step 3"],
    "warnings": ["Warning 1", "Warning 2"],
    "additional_tips": "Any other relevant advice"
}

Key principles:
- Be honest about limitations and risks
- Prioritize farmer welfare and sustainability
- Consider both short-term profit and long-term soil health
- Provide specific, actionable steps
- Use Indian context (mention INR, quintals, local practices)
"""
    
    def chatbot_response(self, user_input: str, location: str) -> Dict:
        """
        Generate AI response based on user query and farm analysis
        
        Args:
            user_input (str): User's question or message
            location (str): Location for farm analysis
        
        Returns:
            dict: Structured chatbot response with recommendations
        """
        try:
            # Step 1: Get comprehensive farm analysis
            farm_data = analyze_farm(location)
            
            # Step 2: Construct detailed context for the AI
            context = self._build_context(user_input, farm_data)
            
            # Step 3: Call OpenAI API
            response = self._call_openai(context)
            
            # Step 4: Parse and validate response
            parsed_response = self._parse_response(response)
            
            # Step 5: Add metadata
            parsed_response["location"] = location
            parsed_response["raw_data"] = {
                "weather": farm_data["weather"],
                "soil": farm_data["soil"],
                "market": farm_data["market"]
            }
            parsed_response["timestamp"] = farm_data.get("timestamp")
            
            return parsed_response
        
        except Exception as e:
            # Return error in consistent format
            return {
                "error": True,
                "message": f"Failed to generate response: {str(e)}",
                "recommended_crop": None,
                "reason": "Unable to process request",
                "risk_level": "Unknown",
                "profit_insight": "Not available",
                "action_steps": ["Please try again or contact support"],
                "warnings": [str(e)]
            }
    
    def _build_context(self, user_input: str, farm_data: Dict) -> str:
        """
        Build comprehensive context string for OpenAI prompt
        
        Args:
            user_input (str): User's question
            farm_data (dict): Complete farm analysis data
        
        Returns:
            str: Formatted context for AI
        """
        context = f"""User Question: {user_input}

Location: {farm_data['location']}

CURRENT WEATHER DATA:
- Temperature: {farm_data['weather']['temperature']}°C
- Humidity: {farm_data['weather']['humidity']}%
- Rainfall: {farm_data['weather']['rainfall']}mm
- Condition: {farm_data['weather']['condition']} ({farm_data['weather']['description']})

SOIL DATA:
- Soil Type: {farm_data['soil']['type']}
- pH Level: {farm_data['soil']['pH']}
- Fertility: {farm_data['soil']['fertility']}
- Nitrogen: {farm_data['soil']['nitrogen']}
- Phosphorus: {farm_data['soil']['phosphorus']}
- Potassium: {farm_data['soil']['potassium']}
- Soil Quality Score: {farm_data['soil_quality_score']}/100

MARKET DATA FOR RECOMMENDED CROP:
- Crop: {farm_data['market']['crop']}
- Current Price: ₹{farm_data['market']['price_per_quintal']}/quintal
- Price Trend: {farm_data['market']['trend']}
- Price Range: ₹{farm_data['market']['min_price']} - ₹{farm_data['market']['max_price']}/quintal

PROFIT ESTIMATE (per acre):
- Expected Yield: {farm_data['profit_estimate'].get('expected_yield_quintals', 'N/A')} quintals
- Total Revenue: ₹{farm_data['profit_estimate'].get('total_revenue', 'N/A')}
- Cultivation Cost: ₹{farm_data['profit_estimate'].get('cultivation_cost', 'N/A')}
- Net Profit: ₹{farm_data['profit_estimate'].get('net_profit', 'N/A')}
- Profit Margin: {farm_data['profit_estimate'].get('profit_margin_percent', 'N/A')}%
- ROI: {farm_data['profit_estimate'].get('roi_percent', 'N/A')}%

ENGINE RECOMMENDATION:
- Primary Crop: {farm_data['recommended_crop']}
- Reasoning: {farm_data['reason']}
- Confidence: {farm_data['confidence']}%
- Risk Level: {farm_data['risk_level']}
- Risk Factors: {', '.join(farm_data['risk_factors'])}

ALTERNATIVE CROPS:
"""
        
        # Add alternative crops
        for alt in farm_data['alternative_crops']:
            context += f"\n- {alt['crop']}: Suitability {alt['suitability_score']}%, Price ₹{alt['price_per_quintal']}/quintal, Trend: {alt['market_trend']}"
        
        context += "\n\nBased on this data, provide your expert advice in the specified JSON format."
        
        return context
    
    def _call_openai(self, context: str) -> str:
        """
        Make API call to OpenAI
        
        Args:
            context (str): Full context for the AI
        
        Returns:
            str: Raw AI response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": context}
                ],
                temperature=0.7,  # Balanced creativity and consistency
                max_tokens=1500,
                response_format={"type": "json_object"}  # Enforce JSON output
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            raise Exception(f"OpenAI API call failed: {str(e)}")
    
    def _parse_response(self, response: str) -> Dict:
        """
        Parse and validate AI response
        
        Args:
            response (str): Raw AI response (JSON string)
        
        Returns:
            dict: Parsed and validated response
        """
        try:
            parsed = json.loads(response)
            
            # Validate required fields
            required_fields = [
                "recommended_crop",
                "reason",
                "risk_level",
                "profit_insight",
                "action_steps",
                "warnings"
            ]
            
            for field in required_fields:
                if field not in parsed:
                    parsed[field] = f"Not provided (missing {field})"
            
            # Ensure action_steps and warnings are lists
            if not isinstance(parsed["action_steps"], list):
                parsed["action_steps"] = [parsed["action_steps"]]
            
            if not isinstance(parsed["warnings"], list):
                parsed["warnings"] = [parsed["warnings"]]
            
            return parsed
        
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse AI response as JSON: {str(e)}")
    
    def get_quick_advice(self, location: str) -> Dict:
        """
        Get quick crop recommendation without user query
        
        Args:
            location (str): Location name
        
        Returns:
            dict: Quick advice response
        """
        default_query = "What crop should I grow right now based on current conditions?"
        return self.chatbot_response(default_query, location)


# Create singleton instance
chatbot = AgriculturalChatbot()


# Convenience function for direct import
def chatbot_response(user_input: str, location: str) -> Dict:
    """
    Convenience function to get chatbot response
    
    Args:
        user_input (str): User's question
        location (str): Location name
    
    Returns:
        dict: Chatbot response
    """
    return chatbot.chatbot_response(user_input, location)
