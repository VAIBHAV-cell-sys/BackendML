# System Architecture Documentation

## Overview

The Climate-Resilient Crop Advisory Chatbot is a modular, production-ready backend system built with FastAPI. It integrates multiple data sources and AI to provide intelligent agricultural recommendations.

## Architecture Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                         Client Layer                           │
│  (Web Frontend, Mobile App, API Consumers)                     │
└───────────────────────────┬────────────────────────────────────┘
                            │
                            │ HTTP/REST
                            ▼
┌────────────────────────────────────────────────────────────────┐
│                      FastAPI Application                       │
│                         (main.py)                              │
│                                                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ /advice  │  │ /analyze │  │ /weather │  │ /crops   │      │
│  │ endpoint │  │ endpoint │  │ endpoint │  │ endpoint │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
│       │             │              │             │            │
└───────┼─────────────┼──────────────┼─────────────┼────────────┘
        │             │              │             │
        │             │              │             │
┌───────▼─────────────▼──────────────▼─────────────▼────────────┐
│                    Business Logic Layer                       │
│                                                                │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────────┐  │
│  │  Chatbot   │  │  Engine    │  │     Services           │  │
│  │ (chatbot.py│  │ (engine.py)│  │  ┌──────────────────┐  │  │
│  │            │  │            │  │  │  weather.py      │  │  │
│  │ - Prompt   │  │ - Decision │  │  │  soil.py         │  │  │
│  │   Building │  │   Logic    │  │  │  mandi.py        │  │  │
│  │ - OpenAI   │  │ - Risk     │  │  └──────────────────┘  │  │
│  │   Call     │  │   Analysis │  │                        │  │
│  │ - Response │  │ - Profit   │  │                        │  │
│  │   Parsing  │  │   Calc     │  │                        │  │
│  └─────┬──────┘  └─────┬──────┘  └────────┬───────────────┘  │
│        │               │                  │                  │
└────────┼───────────────┼──────────────────┼──────────────────┘
         │               │                  │
         │               │                  │
┌────────▼───────────────▼──────────────────▼──────────────────┐
│                    Data & External APIs                       │
│                                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   OpenAI     │  │ OpenWeather  │  │  soil.json   │        │
│  │     API      │  │     API      │  │   (Static)   │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                │
│  ┌──────────────────────────────────────────────────┐        │
│  │      Mock Mandi Database (In-Memory)             │        │
│  │    (Production: Real Mandi API / Database)       │        │
│  └──────────────────────────────────────────────────┘        │
└────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. API Layer (main.py)

**Responsibilities:**
- Route handling and request validation
- CORS configuration
- Global exception handling
- Request/response serialization
- Logging

**Key Features:**
- RESTful endpoints
- Pydantic models for validation
- Auto-generated OpenAPI documentation
- Health checks

### 2. Chatbot Module (chatbot.py)

**Purpose:** AI-powered response generation

**Workflow:**
1. Receive user query + location
2. Call farm analysis engine
3. Build comprehensive context
4. Send prompt to OpenAI
5. Parse and validate JSON response
6. Return structured advice

**Key Methods:**
- `chatbot_response()` - Main entry point
- `_build_context()` - Context preparation
- `_call_openai()` - API integration
- `_parse_response()` - Response validation

### 3. Decision Engine (engine.py)

**Purpose:** Core business logic for crop recommendations

**Analysis Process:**
1. Fetch weather data
2. Fetch soil data
3. Apply rule-based decision logic
4. Calculate risk assessment
5. Get market prices
6. Calculate profit estimates
7. Generate alternatives

**Decision Rules:**
- Rainfall-based crop selection
- Soil type compatibility
- Temperature suitability
- pH optimization
- Fertility adjustments

**Key Methods:**
- `analyze_farm()` - Main analysis
- `_decide_crop()` - Decision logic
- `_assess_risk()` - Risk calculation
- `_get_alternative_crops()` - Alternatives

### 4. Service Layer

#### Weather Service (weather.py)

**Integration:** OpenWeather API

**Data Fetched:**
- Temperature (°C)
- Humidity (%)
- Rainfall (mm)
- Weather condition
- Wind speed
- Pressure

**Error Handling:**
- Location not found
- API timeout
- Invalid API key
- Rate limiting

#### Soil Service (soil.py)

**Data Source:** JSON database (data/soil.json)

**Data Points:**
- Soil type
- pH level
- Fertility rating
- NPK levels
- Organic matter

**Features:**
- Exact location matching
- Partial matching fallback
- Default values
- Quality scoring
- Recommendations

#### Mandi Service (mandi.py)

**Current:** Mock data (13 crops)

**Data Provided:**
- Current price (₹/quintal)
- Price trend
- Price range
- Market variation

**Features:**
- Daily price fluctuation simulation
- Profit estimation
- Crop comparison
- ROI calculation

## Data Flow

### Request Flow (GET /advice)

```
1. Client Request
   ↓
2. FastAPI Validation (Pydantic)
   ↓
3. chatbot_response() called
   ↓
4. analyze_farm() called
   ├→ get_weather() → OpenWeather API
   ├→ get_soil() → soil.json
   └→ get_price() → Mock DB
   ↓
5. Decision Engine Processing
   ├→ Apply rules
   ├→ Calculate risk
   └→ Estimate profit
   ↓
6. Build AI Context
   ↓
7. OpenAI API Call
   ↓
8. Parse JSON Response
   ↓
9. Return to Client
```

### Data Dependencies

```
┌──────────────┐
│  User Query  │
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌──────────────┐
│   Location   │────▶│   Weather    │──▶ OpenWeather API
└──────┬───────┘     └──────────────┘
       │
       │             ┌──────────────┐
       ├────────────▶│     Soil     │──▶ soil.json
       │             └──────────────┘
       │
       │             ┌──────────────┐
       └────────────▶│    Mandi     │──▶ Mock Database
                     └──────────────┘
```

## Configuration Management

### Environment Variables (.env)

```
OPENWEATHER_API_KEY → Weather service
OPENAI_API_KEY      → Chatbot service
DEBUG               → Logging level
HOST                → Server binding
PORT                → Server port
```

### Config Class (config.py)

**Features:**
- Environment variable loading
- Validation on startup
- Default values
- Type conversion

## Error Handling Strategy

### Levels of Error Handling

1. **Input Validation**
   - Pydantic models
   - Type checking
   - Required fields

2. **Service Level**
   - API failures
   - Timeout handling
   - Data not found

3. **Business Logic**
   - Invalid conditions
   - Missing data
   - Calculation errors

4. **Global Handler**
   - Unexpected exceptions
   - Logging
   - User-friendly messages

## Security Considerations

### Current Implementation

1. **API Key Protection**
   - Environment variables
   - Not in code
   - .gitignore .env

2. **Input Validation**
   - Pydantic models
   - Type safety
   - XSS prevention

3. **CORS**
   - Configurable origins
   - Wildcard in development

### Production Recommendations

1. **Rate Limiting**
   - Per-IP limits
   - API key quotas
   - Distributed rate limiter

2. **Authentication**
   - API keys for clients
   - JWT tokens
   - OAuth2 integration

3. **HTTPS**
   - SSL/TLS certificates
   - Secure headers
   - HSTS

4. **Database**
   - Connection pooling
   - Query parameterization
   - Access control

## Scalability

### Current Architecture

- **Stateless** - No session storage
- **Horizontal Scaling** - Can run multiple instances
- **Caching Ready** - Add Redis for weather/soil data

### Scaling Path

```
Single Server
    ↓
Load Balancer + Multiple Servers
    ↓
Microservices (Weather, Soil, Mandi, AI separate)
    ↓
Kubernetes Cluster + Auto-scaling
```

## Performance Optimization

### Current Optimizations

1. **Singleton Services**
   - Reuse service instances
   - Avoid repeated initialization

2. **Async-Ready**
   - FastAPI async support
   - Can add async/await

3. **Efficient Data Structures**
   - Dictionary lookups
   - JSON parsing
   - Minimal processing

### Future Improvements

1. **Caching**
   - Redis for weather (15 min TTL)
   - In-memory soil cache
   - Price caching (hourly)

2. **Database**
   - PostgreSQL for persistence
   - Connection pooling
   - Indexed queries

3. **Background Tasks**
   - Celery for long operations
   - Scheduled weather updates
   - Batch processing

## Monitoring & Observability

### Logging

**Current:**
- Python logging module
- Console output
- Log levels (INFO, ERROR)

**Production:**
- Structured logging (JSON)
- Log aggregation (ELK, Datadog)
- Alert on errors

### Metrics

**Recommended:**
- Request rate
- Response time
- Error rate
- API call success rate
- Cache hit ratio

## Testing Strategy

### Current Tests (test_api.py)

- Endpoint availability
- Response format
- Error handling

### Recommended Testing

1. **Unit Tests**
   - Service methods
   - Decision logic
   - Profit calculations

2. **Integration Tests**
   - API endpoints
   - External APIs
   - Database

3. **Load Tests**
   - Concurrent requests
   - Response time
   - Resource usage

## Deployment Architecture

### Development

```
Local Machine
├── Python virtual environment
├── .env file
└── uvicorn server
```

### Production

```
Cloud Platform (AWS/GCP/Azure)
├── Docker Container
├── Load Balancer
├── Auto-scaling Group
├── RDS Database
├── Redis Cache
├── S3/Cloud Storage
└── CloudWatch/Monitoring
```

## API Versioning

**Current:** v1 (implicit)

**Future:**
- `/v1/advice` (current API)
- `/v2/advice` (enhanced features)
- Header-based versioning

## Data Models

### Farm Analysis Output

```python
{
  "location": str,
  "recommended_crop": str,
  "reason": str,
  "confidence": int (0-100),
  "risk_level": str,
  "risk_factors": [str],
  "weather": {...},
  "soil": {...},
  "market": {...},
  "profit_estimate": {...},
  "alternative_crops": [{...}]
}
```

### Chatbot Response

```python
{
  "recommended_crop": str,
  "reason": str,
  "risk_level": str,
  "profit_insight": str,
  "action_steps": [str],
  "warnings": [str],
  "raw_data": {...}
}
```

## Extension Points

### Adding New Data Sources

1. Create service in `services/`
2. Add integration in `engine.py`
3. Update decision logic
4. Add endpoint in `main.py`

### Adding New Crops

1. Update `mandi.py` prices
2. Add yield data
3. Add cultivation costs
4. Update decision rules

### Adding ML Models

1. Train model separately
2. Save model file
3. Create prediction service
4. Integrate in engine

## Dependencies

### Core
- FastAPI - Web framework
- Uvicorn - ASGI server
- Pydantic - Validation

### External APIs
- OpenAI - AI responses
- OpenWeather - Weather data

### Utilities
- requests - HTTP client
- python-dotenv - Config

## Future Enhancements

1. **Database Integration**
   - User history
   - Query analytics
   - Persistent storage

2. **Real Mandi API**
   - Government mandi APIs
   - Live price updates
   - Historical trends

3. **ML Integration**
   - Yield prediction models
   - Price forecasting
   - Disease detection

4. **Multi-language**
   - Hindi, Tamil, Telugu
   - Regional crop names
   - Local units

5. **Mobile Integration**
   - SMS gateway
   - WhatsApp bot
   - USSD support

---

**Last Updated:** March 2026
**Version:** 1.0.0
