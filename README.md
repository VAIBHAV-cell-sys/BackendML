# Climate-Resilient Crop Advisory Chatbot - Backend

A comprehensive FastAPI-based backend system that provides AI-powered agricultural advisory services for Indian farmers. The system integrates real-time weather data, soil information, market prices, and decision-making logic to recommend optimal crops.

## 🌟 Features

- **AI-Powered Chatbot**: OpenAI integration for natural language responses
- **Real-time Weather Data**: OpenWeather API integration
- **Soil Database**: Comprehensive soil data for Indian locations
- **Market Prices**: Mock mandi price system for major crops
- **Decision Engine**: Rule-based crop recommendation system
- **Risk Assessment**: Automated risk evaluation based on conditions
- **Profit Estimation**: Calculate expected returns per acre
- **RESTful API**: Complete FastAPI endpoints with documentation

## 📁 Project Structure

```
backend/
│
├── main.py                 # FastAPI application & endpoints
├── engine.py               # Core decision logic
├── chatbot.py              # OpenAI integration
├── config.py               # Configuration & API keys
├── requirements.txt        # Python dependencies
│
├── services/
│   ├── weather.py          # OpenWeather API service
│   ├── soil.py             # Soil data service
│   └── mandi.py            # Market price service
│
└── data/
    └── soil.json           # Soil database (15+ locations)
```

## 🚀 Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- OpenWeather API key (free tier available)
- OpenAI API key

### 2. Install Dependencies

```bash
# Navigate to backend directory
cd backend

# Install required packages
pip install -r requirements.txt
```

### 3. Configure API Keys

Create a `.env` file in the backend directory:

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
OPENWEATHER_API_KEY=your_actual_openweather_key
OPENAI_API_KEY=your_actual_openai_key
DEBUG=False
HOST=0.0.0.0
PORT=8000
```

#### How to Get API Keys:

**OpenWeather API:**
1. Visit https://openweathermap.org/api
2. Sign up for free account
3. Generate API key from dashboard

**OpenAI API:**
1. Visit https://platform.openai.com/
2. Create account or login
3. Navigate to API keys section
4. Create new secret key

### 4. Run the Server

```bash
# Development mode (with auto-reload)
python main.py

# OR using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server will start at: `http://localhost:8000`

### 5. Verify Installation

Open browser and navigate to:
- API Docs: `http://localhost:8000/docs`
- Alternative Docs: `http://localhost:8000/redoc`
- Health Check: `http://localhost:8000/health`

## 📡 API Endpoints

### Main Endpoints

#### 1. Get Crop Advice (GET)
```http
GET /advice?message=What crop should I plant?&location=Pune
```

**Response:**
```json
{
  "recommended_crop": "Cotton",
  "reason": "Based on current weather and soil conditions...",
  "risk_level": "Medium",
  "profit_insight": "Expected profit of ₹45,000 per acre...",
  "action_steps": [
    "Prepare field with proper plowing",
    "Apply base fertilizers (DAP)",
    "Ensure irrigation availability"
  ],
  "warnings": [
    "Monitor for bollworm infestation",
    "Maintain soil moisture"
  ],
  "raw_data": {
    "weather": {...},
    "soil": {...},
    "market": {...}
  }
}
```

#### 2. Get Crop Advice (POST)
```http
POST /advice
Content-Type: application/json

{
  "message": "What is the best crop for my farm?",
  "location": "Delhi"
}
```

#### 3. Farm Analysis
```http
GET /analyze/Pune
```

Returns comprehensive analysis without AI interpretation.

#### 4. Weather Data
```http
GET /weather/Mumbai
```

**Response:**
```json
{
  "temp": 28.5,
  "humidity": 75,
  "rain": 2.3,
  "condition": "Rain",
  "description": "moderate rain",
  "feels_like": 29.1,
  "wind_speed": 3.5
}
```

#### 5. Soil Data
```http
GET /soil/Bangalore
```

**Response:**
```json
{
  "soil_type": "Red Soil",
  "pH": 6.5,
  "fertility": "Medium",
  "nitrogen": "Medium",
  "phosphorus": "Low",
  "potassium": "Medium",
  "organic_matter": 1.8
}
```

#### 6. Market Price
```http
GET /price/wheat
```

**Response:**
```json
{
  "crop": "Wheat",
  "price": 2125,
  "current_price": 2143.50,
  "unit": "quintal",
  "trend": "stable",
  "min_price": 2050,
  "max_price": 2200
}
```

#### 7. Compare Crops
```http
GET /compare-crops/Pune?crops=wheat,rice,cotton&area_acres=2
```

#### 8. List All Crops
```http
GET /crops
```

#### 9. Quick Advice
```http
GET /quick-advice/Jaipur
```

## 🧪 Testing the API

### Using cURL

```bash
# Get advice
curl "http://localhost:8000/advice?message=Should%20I%20plant%20rice?&location=Kolkata"

# Get analysis
curl "http://localhost:8000/analyze/Chennai"

# Get weather
curl "http://localhost:8000/weather/Hyderabad"
```

### Using Python

```python
import requests

# Get crop advice
response = requests.get(
    "http://localhost:8000/advice",
    params={
        "message": "What crop is profitable now?",
        "location": "Pune"
    }
)
print(response.json())
```

### Using Browser

Navigate to `http://localhost:8000/docs` for interactive API testing.

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENWEATHER_API_KEY` | OpenWeather API key | - | Yes |
| `OPENAI_API_KEY` | OpenAI API key | - | Yes |
| `DEBUG` | Enable debug mode | False | No |
| `HOST` | Server host | 0.0.0.0 | No |
| `PORT` | Server port | 8000 | No |

### Modifying Decision Logic

Edit `engine.py` to customize crop recommendation rules:

```python
# Example: Add new crop rule
if rainfall < 1 and temp > 35:
    crop = "Bajra"
    reason = "Hot and dry conditions suit bajra"
    confidence = 90
```

### Adding New Crops

Edit `services/mandi.py`:

```python
self.base_prices["new_crop"] = {
    "price": 3000,
    "unit": "quintal",
    "trend": "rising",
    "min_price": 2800,
    "max_price": 3200
}
```

### Adding Soil Data

Edit `data/soil.json`:

```json
{
  "locations": {
    "NewCity": {
      "soil_type": "Alluvial",
      "pH": 7.0,
      "fertility": "High",
      "nitrogen": "High",
      "phosphorus": "Medium",
      "potassium": "Medium",
      "organic_matter": 2.0
    }
  }
}
```

## ⚠️ Error Handling

The API handles common errors:

### Invalid Location
```json
{
  "detail": "Location 'InvalidCity' not found"
}
```

### Missing API Keys
```json
{
  "detail": "Configuration errors: OPENWEATHER_API_KEY is not set"
}
```

### Weather API Failure
```json
{
  "detail": "Failed to fetch weather data: Connection timeout"
}
```

## 📊 System Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│      FastAPI Main.py            │
│  (API Endpoints & Validation)   │
└──────┬──────────────────────────┘
       │
       ├──────┬──────┬──────┬──────┐
       ▼      ▼      ▼      ▼      ▼
   ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐
   │Chat│ │Eng │ │Wea │ │Soil│ │Man │
   │bot │ │ine │ │ther│ │    │ │di  │
   └─┬──┘ └─┬──┘ └─┬──┘ └─┬──┘ └─┬──┘
     │      │      │      │      │
     ▼      ▼      ▼      ▼      ▼
  ┌───────────────────────────────┐
  │    External APIs & Data       │
  │  (OpenAI, OpenWeather, JSON)  │
  └───────────────────────────────┘
```

## 🔒 Security Considerations

1. **API Keys**: Never commit `.env` file to version control
2. **CORS**: Configure allowed origins in production
3. **Rate Limiting**: Implement rate limiting for production
4. **Input Validation**: All inputs are validated via Pydantic
5. **Error Messages**: Sanitized error messages in production

## 🚀 Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Setup

```bash
# Production environment variables
DEBUG=False
OPENWEATHER_API_KEY=prod_key_here
OPENAI_API_KEY=prod_key_here
```

## 📝 Logging

The system logs all important events:

```
2024-01-15 10:30:45 - INFO - Advice request: location=Pune
2024-01-15 10:30:46 - INFO - Advice generated successfully for Pune
```

## 🐛 Troubleshooting

### Issue: "OPENWEATHER_API_KEY is not set"
**Solution**: Create `.env` file with valid API keys

### Issue: "Location not found"
**Solution**: Use exact city names (e.g., "Mumbai" not "Bombay")

### Issue: "OpenAI API call failed"
**Solution**: Check API key validity and account credits

### Issue: "Module not found"
**Solution**: Run `pip install -r requirements.txt`

## 📚 Available Crops

wheat, rice, bajra, maize, cotton, sugarcane, groundnut, soybean, jowar, pulses, potato, onion, tomato

## 🌍 Supported Locations

Delhi, Mumbai, Bangalore, Pune, Jaipur, Hyderabad, Chennai, Kolkata, Lucknow, Patna, Ahmedabad, Chandigarh, Indore, Nagpur, Bhopal

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📄 License

MIT License - See LICENSE file for details

## 👥 Support

For issues or questions:
- Create GitHub issue
- Check API documentation at `/docs`
- Review logs for error details

## 🎯 Future Enhancements

- [ ] Real mandi API integration
- [ ] Machine learning crop prediction
- [ ] Historical weather analysis
- [ ] Multi-language support
- [ ] SMS/WhatsApp integration
- [ ] Database for user queries
- [ ] Advanced analytics dashboard
- [ ] Mobile app integration

---

**Built with ❤️ for Indian Farmers**
# BackendML
