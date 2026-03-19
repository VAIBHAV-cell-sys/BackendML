# Quick Start Guide

Get the Climate-Resilient Crop Advisory API running in 5 minutes!

## 📋 Prerequisites

- Python 3.8+ installed
- Internet connection
- Text editor

## 🚀 Setup Steps

### Step 1: Navigate to Backend Directory

```bash
cd backend
```

### Step 2: Get API Keys

You need two free API keys:

#### OpenWeather API Key
1. Go to https://openweathermap.org/api
2. Click "Sign Up" (free account)
3. Verify email
4. Go to "API Keys" section
5. Copy your API key

#### OpenAI API Key
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to "API Keys"
4. Click "Create new secret key"
5. Copy and save the key (you won't see it again!)

### Step 3: Configure Environment

#### Option A: Automatic (Recommended)

**Linux/Mac:**
```bash
./run.sh
```

**Windows:**
```bash
run.bat
```

The script will:
- Create `.env` file
- Set up virtual environment
- Install dependencies
- Prompt for API keys
- Start the server

#### Option B: Manual Setup

1. **Create virtual environment:**
```bash
python -m venv venv
```

2. **Activate virtual environment:**

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp .env.example .env
```

5. **Edit `.env` file:**
```env
OPENWEATHER_API_KEY=your_actual_key_here
OPENAI_API_KEY=your_actual_key_here
```

6. **Start server:**
```bash
python main.py
```

### Step 4: Verify Installation

1. **Check Health:**
   - Open browser: http://localhost:8000/health
   - Should see: `{"status": "healthy", ...}`

2. **Open API Documentation:**
   - http://localhost:8000/docs
   - Interactive Swagger UI

3. **Test First Request:**
   - In browser: http://localhost:8000/weather/Delhi
   - Should see weather data

## 🧪 Test the API

### Quick Test

```bash
# In a new terminal (keep server running)
python test_api.py
```

This runs 11 automated tests covering all endpoints.

### Manual Testing

#### Test 1: Get Weather
```bash
curl "http://localhost:8000/weather/Mumbai"
```

#### Test 2: Get Crop Advice
```bash
curl "http://localhost:8000/advice?message=What%20crop%20should%20I%20plant?&location=Pune"
```

#### Test 3: Farm Analysis
```bash
curl "http://localhost:8000/analyze/Bangalore"
```

## 📱 Example Requests

### Using Browser

Just paste these URLs:

```
http://localhost:8000/advice?message=Should I plant rice?&location=Kolkata

http://localhost:8000/crops

http://localhost:8000/quick-advice/Delhi
```

### Using Python

```python
import requests

# Get crop advice
response = requests.get(
    "http://localhost:8000/advice",
    params={
        "message": "What is the most profitable crop?",
        "location": "Pune"
    }
)

print(response.json())
```

### Using cURL

```bash
# POST request
curl -X POST "http://localhost:8000/advice" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Best crop for high rainfall?",
    "location": "Chennai"
  }'
```

### Using Postman

1. Import this request:
   - Method: GET
   - URL: `http://localhost:8000/advice`
   - Params: 
     - `message`: "What crop should I grow?"
     - `location`: "Jaipur"

2. Send request
3. View JSON response

## 🎯 Key Endpoints to Try

| Endpoint | What It Does | Example |
|----------|-------------|---------|
| `/advice` | Get AI crop advice | `?message=What to plant&location=Delhi` |
| `/analyze/{location}` | Farm analysis | `/analyze/Mumbai` |
| `/weather/{location}` | Current weather | `/weather/Bangalore` |
| `/soil/{location}` | Soil data | `/soil/Pune` |
| `/price/{crop}` | Market price | `/price/wheat` |
| `/crops` | All crops list | `/crops` |
| `/compare-crops/{location}` | Compare profits | `?crops=wheat,rice,cotton` |

## 🐛 Troubleshooting

### Server won't start

**Problem:** `OPENWEATHER_API_KEY is not set`
- **Solution:** Edit `.env` file and add your API keys

**Problem:** `Port 8000 already in use`
- **Solution:** Change port in `.env`: `PORT=8001`
- Or find process: `lsof -i :8000` and kill it

**Problem:** `Module not found`
- **Solution:** Install dependencies: `pip install -r requirements.txt`

### API returns errors

**Problem:** `Location 'XYZ' not found`
- **Solution:** Use valid city names: Delhi, Mumbai, Pune, etc.
- Check supported locations in README.md

**Problem:** `OpenAI API call failed`
- **Solution:** 
  - Verify API key is correct
  - Check your OpenAI account has credits
  - Ensure internet connection

**Problem:** `Weather API timeout`
- **Solution:**
  - Check internet connection
  - Verify OpenWeather API key
  - Try different location

## 💡 What's Next?

### Explore the API
1. Open http://localhost:8000/docs
2. Try "Try it out" button on each endpoint
3. See live examples

### Read Documentation
- `README.md` - Complete guide
- `ARCHITECTURE.md` - System design
- API docs at `/docs` endpoint

### Customize
- Add new crops in `services/mandi.py`
- Modify decision logic in `engine.py`
- Add locations in `data/soil.json`

### Deploy
- See README.md for production deployment
- Docker configuration available
- Cloud deployment guides

## 📞 Support

### Issues?
1. Check logs in console where server is running
2. Try test script: `python test_api.py`
3. Review error messages
4. Check API key configuration

### Common Solutions
- Restart server: `Ctrl+C` then `python main.py`
- Clear Python cache: `find . -name "*.pyc" -delete`
- Reinstall deps: `pip install -r requirements.txt --force-reinstall`

## ✅ Success Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] API keys configured in `.env`
- [ ] Server starts without errors
- [ ] Health check returns 200
- [ ] Can access `/docs` page
- [ ] Weather endpoint works
- [ ] Advice endpoint returns data
- [ ] Tests pass

If all checked, you're ready to go! 🎉

## 🔥 Pro Tips

1. **Keep server running** in one terminal
2. **Test in another** terminal window
3. **Use the docs** at `/docs` for easy testing
4. **Check logs** for debugging
5. **Start simple** - test weather first, then advice

---

**Time to First API Call:** ~5 minutes

Happy coding! 🚀
