# Machine Learning Crop Prediction System

## 🎯 Overview

This ML system enhances your chatbot with **data-driven crop predictions** based on historical crop success/failure patterns. It learns from past data to predict which crops will succeed under current conditions.

---

## 📁 Project Structure

```
backend/
├── ml_crop_prediction.py          # Core ML model (Random Forest)
├── ml_integration.py               # Integration with FastAPI backend
├── main_ml_enhanced.py             # Enhanced endpoints for your main.py
├── data_collection.py              # Historical data collection tools
│
├── models/
│   └── crop_prediction_model.pkl   # Trained ML model (auto-generated)
│
├── crop_historical_data.csv        # Historical training data
└── data_collection_template.csv    # Template for data entry
```

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install scikit-learn pandas numpy joblib
```

### Step 2: Train the Model

```bash
# This creates sample data and trains the model
python ml_crop_prediction.py
```

**Output:**
- ✅ Creates `crop_historical_data.csv` (5000 sample records)
- ✅ Trains Random Forest model
- ✅ Saves model to `models/crop_prediction_model.pkl`
- ✅ Shows accuracy metrics and feature importance

### Step 3: Integrate with Your Backend

Add to your existing `main.py`:

```python
# Add these imports at the top
from ml_integration import get_ml_prediction, compare_with_rules, ml_service
from datetime import datetime

# Copy all endpoints from main_ml_enhanced.py
# Or run the enhanced main file directly
```

### Step 4: Test ML Endpoints

```bash
# Start your backend
python main.py

# Test ML prediction
curl "http://localhost:8000/ml-predict/Pune"

# Test hybrid prediction (ML + Rule-based)
curl "http://localhost:8000/hybrid-predict/Mumbai"

# Get ML-powered advice
curl "http://localhost:8000/advice-ml?message=What%20to%20plant&location=Delhi&use_ml=true"
```

---

## 📊 How It Works

### 1. **Historical Data Learning**

The model learns from past crop outcomes:

```
Input Features:
├── Weather: temperature, humidity, rainfall, wind, pressure, clouds
├── Soil: pH, nitrogen, phosphorus, potassium, organic matter
└── Temporal: season, month

Output:
└── Crop recommendation + confidence score
```

### 2. **Training Process**

```python
Historical Data (5000 records)
    ↓
Feature Engineering
    ↓
Random Forest Training (200 trees)
    ↓
Cross-Validation (5-fold)
    ↓
Model Saved → crop_prediction_model.pkl
```

### 3. **Prediction Pipeline**

```
Current Weather + Soil Data
    ↓
Feature Preparation
    ↓
ML Model Inference
    ↓
Top 3 Crop Recommendations + Confidence Scores
```

---

## 🔌 API Endpoints

### 1. ML Prediction

```http
GET /ml-predict/{location}
```

**Example:**
```bash
curl "http://localhost:8000/ml-predict/Pune"
```

**Response:**
```json
{
  "timestamp": "2026-03-18T10:00:00",
  "primary_recommendation": "Rice",
  "confidence": 84.56,
  "all_recommendations": [
    {"crop": "Rice", "confidence": 84.56},
    {"crop": "Maize", "confidence": 9.08},
    {"crop": "Wheat", "confidence": 3.21}
  ],
  "location": "Pune",
  "method": "machine_learning"
}
```

### 2. Hybrid Prediction (ML + Rules)

```http
GET /hybrid-predict/{location}
```

**Example:**
```bash
curl "http://localhost:8000/hybrid-predict/Mumbai"
```

**Response:**
```json
{
  "rule_based": {
    "crop": "Cotton",
    "confidence": 85,
    "reason": "Black soil + moderate rain"
  },
  "machine_learning": {
    "crop": "Rice",
    "confidence": 84.56,
    "top_3": [...]
  },
  "comparison": {
    "agreement": false,
    "verdict": "Different recommendations - Consider both options"
  },
  "recommendation": {
    "final_crop": "Cotton",
    "method": "rule-based",
    "confidence": "Moderate"
  }
}
```

### 3. ML-Powered Advice

```http
GET /advice-ml?message={query}&location={city}&use_ml=true
```

**Example:**
```bash
curl "http://localhost:8000/advice-ml?message=Best%20crop%20now&location=Delhi&use_ml=true"
```

### 4. Model Management

```http
GET /ml-model-info          # Get model statistics
POST /ml-train              # Retrain model with new data
```

---

## 📚 Using Your Own Historical Data

### Method 1: Manual Data Entry

1. **Create template:**
```bash
python data_collection.py
```

2. **Fill the CSV:**
Open `data_collection_template.csv` and add your records:

```csv
date,location,crop,temperature,humidity,rainfall,...,success
2023-06-15,Pune,Rice,28.5,75,8.5,...,Yes
2023-07-20,Jaipur,Bajra,32,40,0.5,...,Yes
2023-08-10,Delhi,Wheat,22,55,1.2,...,No
```

3. **Format and train:**
```python
from data_collection import HistoricalDataCollector

collector = HistoricalDataCollector()
collector.format_collected_data('your_data.csv', 'formatted_data.csv')

# Train with your data
from ml_crop_prediction import CropPredictionModel
model = CropPredictionModel()
model.train('formatted_data.csv')
model.save_model()
```

### Method 2: API Integration

Fetch historical weather from APIs:

```python
# Example: Visual Crossing Weather API
import requests

def fetch_historical_weather(location, start_date, end_date):
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}/{start_date}/{end_date}"
    
    params = {
        'key': 'YOUR_API_KEY',
        'unitGroup': 'metric',
        'include': 'days'
    }
    
    response = requests.get(url, params=params)
    return response.json()
```

**Recommended APIs:**
- **Visual Crossing:** Historical weather data
- **Meteostat:** Free weather data library
- **OpenWeather History:** Historical weather (paid)

### Method 3: Government Data

**Indian Government Sources:**
- **AGMARKNET:** Market prices and crop arrivals
- **IMD:** Indian Meteorological Department weather data
- **Soil Health Card Portal:** Soil test results
- **NFSM:** Crop statistics and yields

---

## 🎯 Model Performance

### Current Model (Sample Data)

```
Accuracy: 42.73%
Cross-Validation: 44.48% (±1.26%)

Top Performing Crops:
├── Rice: 85% precision
├── Bajra: 76% precision
├── Wheat: 61% precision
```

### Expected Performance (Real Data)

With **1000+ real historical records**:
- Expected accuracy: **70-80%**
- Confidence scores: More reliable
- Better generalization

---

## 🔧 Configuration

### Tuning the Model

Edit `ml_crop_prediction.py`:

```python
# Adjust Random Forest parameters
self.model = RandomForestClassifier(
    n_estimators=200,      # Number of trees (↑ = better, slower)
    max_depth=20,          # Tree depth (↑ = complex, risk overfit)
    min_samples_split=5,   # Min samples to split (↑ = simpler)
    random_state=42
)
```

### Feature Engineering

Add new features in `ml_integration.py`:

```python
features = {
    'temperature': weather_data['temp'],
    'humidity': weather_data['humidity'],
    # Add custom features:
    'temp_humidity_ratio': weather_data['temp'] / weather_data['humidity'],
    'soil_nutrient_score': (nitrogen + phosphorus + potassium) / 3
}
```

---

## 📈 Monitoring & Improvement

### Track Predictions

Log predictions vs actual outcomes:

```python
# In your main.py
@app.post("/feedback/{prediction_id}")
async def record_outcome(prediction_id: str, actual_crop: str, success: bool):
    """Record actual outcome for model improvement"""
    # Save to database
    # Periodically retrain model with new data
```

### Retrain Periodically

```bash
# Weekly/monthly retraining
curl -X POST "http://localhost:8000/ml-train"
```

### Monitor Metrics

```python
# Get model performance
curl "http://localhost:8000/ml-model-info"
```

---

## 🐛 Troubleshooting

### Issue 1: Low Accuracy

**Cause:** Insufficient or low-quality training data  
**Solution:**
- Collect more historical records (aim for 1000+)
- Balance success/failure cases (50/50 ratio)
- Verify data quality (no missing values)

### Issue 2: Model Not Loading

**Cause:** Model file not found  
**Solution:**
```bash
python ml_crop_prediction.py  # This will train and save model
```

### Issue 3: Different Results from Rules

**Cause:** ML learns different patterns than hardcoded rules  
**Solution:**
- Use hybrid endpoint to see both
- Trust ML when it has high confidence (>70%)
- Use comparison to understand differences

---

## 🔄 Integration Flow

```
User Request
    ↓
FastAPI Backend
    ↓
┌─────────────────┬─────────────────┐
│   Rule-Based    │   ML-Based      │
│   Engine        │   Model         │
└────────┬────────┴────────┬────────┘
         │                 │
         └────────┬────────┘
                  ↓
           Hybrid Result
                  ↓
           AI Chatbot (GPT-4)
                  ↓
           JSON Response
```

---

## 💡 Best Practices

### 1. Data Collection

✅ **DO:**
- Collect data from multiple seasons
- Include both successes and failures
- Record actual field conditions
- Verify data accuracy

❌ **DON'T:**
- Use only successful cases
- Rely on synthetic data long-term
- Skip data validation
- Mix different locations without context

### 2. Model Usage

✅ **DO:**
- Use hybrid predictions for critical decisions
- Monitor prediction accuracy over time
- Retrain with new data regularly
- Show confidence scores to users

❌ **DON'T:**
- Blindly trust low-confidence predictions
- Ignore rule-based recommendations
- Deploy without testing
- Forget to version control models

### 3. Production Deployment

✅ **DO:**
- Set up model versioning
- Log all predictions
- Implement fallback to rules if ML fails
- Cache predictions for same conditions

❌ **DON'T:**
- Train in production
- Skip error handling
- Ignore model drift
- Expose raw ML errors to users

---

## 📞 Support

### Common Questions

**Q: How much data do I need?**  
A: Minimum 500 records, ideal 1000+ for good accuracy

**Q: Can I use this without historical data?**  
A: Yes, start with rule-based system, collect data over time

**Q: Which is better - ML or rules?**  
A: Use hybrid! ML learns patterns, rules provide safety net

**Q: How often should I retrain?**  
A: Monthly with new data, or when accuracy drops below 60%

---

## 🚀 Next Steps

1. ✅ Train model with sample data
2. ✅ Test ML endpoints
3. ✅ Integrate with your main.py
4. 📊 Start collecting real historical data
5. 🔄 Retrain with real data after 100+ records
6. 📈 Monitor and improve continuously

---

**🎉 Your ML-powered crop prediction system is ready!**

The model will get smarter as you collect more real-world data. Start with the hybrid approach to leverage both rule-based reliability and ML learning capabilities.
