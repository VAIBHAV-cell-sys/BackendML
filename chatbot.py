import json
from typing import Dict
from openai import OpenAI
from config import Config
from engine import analyze_farm


class AgriculturalChatbot:
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL

        self.system_prompt = """
You are an AI agriculture advisor for Indian farmers.

Return ONLY JSON in this format:
{
    "recommended_crop": "",
    "reason": "",
    "risk_level": "",
    "profit_insight": "",
    "action_steps": [],
    "warnings": [],
    "additional_tips": ""
}
"""

    def chatbot_response(self, user_input: str, location: str) -> Dict:
        try:
            farm_data = analyze_farm(location)

            context = self._build_context(user_input, farm_data)

            raw_response = self._call_openai(context)

            parsed = self._parse_response(raw_response)

            parsed["location"] = location
            parsed["timestamp"] = farm_data.get("timestamp")

            return parsed

        except Exception as e:
            return {
                "error": True,
                "message": str(e),
                "recommended_crop": None,
                "reason": "Error occurred",
                "risk_level": "Unknown",
                "profit_insight": "N/A",
                "action_steps": ["Retry"],
                "warnings": [str(e)]
            }

    def _build_context(self, user_input: str, farm_data: Dict) -> str:
        return f"""
User Question: {user_input}

Location: {farm_data['location']}

Weather:
Temp: {farm_data['weather']['temperature']}°C
Humidity: {farm_data['weather']['humidity']}%
Rainfall: {farm_data['weather']['rainfall']}mm

Soil:
Type: {farm_data['soil']['type']}
pH: {farm_data['soil']['pH']}
Fertility: {farm_data['soil']['fertility']}

Market:
Crop: {farm_data['market']['crop']}
Price: ₹{farm_data['market']['price_per_quintal']}

Recommended Crop: {farm_data['recommended_crop']}
Reason: {farm_data['reason']}
Risk: {farm_data['risk_level']}

Respond in JSON only.
"""

    def _call_openai(self, context: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": context}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"OpenAI Error: {str(e)}")

    def _parse_response(self, response: str) -> Dict:
        try:
            try:
                parsed = json.loads(response)
            except:
                start = response.find("{")
                end = response.rfind("}") + 1
                parsed = json.loads(response[start:end])

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
                    parsed[field] = "Not provided"

            if not isinstance(parsed["action_steps"], list):
                parsed["action_steps"] = [parsed["action_steps"]]

            if not isinstance(parsed["warnings"], list):
                parsed["warnings"] = [parsed["warnings"]]

            return parsed

        except Exception as e:
            raise Exception(f"Parse Error: {str(e)}")

    def get_quick_advice(self, location: str) -> Dict:
        return self.chatbot_response(
            "What crop should I grow right now?", location
        )


chatbot = AgriculturalChatbot()


def chatbot_response(user_input: str, location: str) -> Dict:
    return chatbot.chatbot_response(user_input, location)
