from ml_integration import get_ml_prediction, compare_with_rules, ml_service
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict
import logging
from datetime import datetime

# Import services
from chatbot import chatbot_response, chatbot
from engine import analyze_farm
from services.weather import get_weather
from services.soil import get_soil
from services.mandi import get_price, mandi_service
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Climate-Resilient Crop Advisory API",
    description="AI-powered agricultural advisory system for Indian farmers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class AdviceRequest(BaseModel):
    """Request model for advice endpoint"""
    message: str = Field(..., description="User's question or query")
    location: str = Field(..., description="Location/city name")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "What crop should I plant this season?",
                "location": "Pune"
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    timestamp: str
    version: str


# API Endpoints

@app.get("/", tags=["System"])
async def root():
    """
    Root endpoint - API information
    """
    return {
        "message": "Climate-Resilient Crop Advisory API",
        "version": "1.0.0",
        "endpoints": {
            "advice": "/advice - Get crop advice (GET)",
            "advice_post": "/advice - Get crop advice (POST)",
            "analyze": "/analyze/{location} - Get farm analysis",
            "weather": "/weather/{location} - Get weather data",
            "soil": "/soil/{location} - Get soil data",
            "price": "/price/{crop} - Get crop price",
            "crops": "/crops - List all available crops",
            "health": "/health - System health check",
            "docs": "/docs - Interactive API documentation"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Health check endpoint to verify API is running
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.get("/advice", tags=["Chatbot"])
async def get_advice(
    message: str = Query(..., description="User's question about farming"),
    location: str = Query(..., description="Location/city name")
):
    """
    Main chatbot endpoint - Get AI-powered crop advisory
    
    Returns structured JSON response with:
    - Recommended crop
    - Detailed reasoning
    - Risk assessment
    - Profit insights
    - Action steps
    - Warnings
    - Supporting data (weather, soil, market)
    """
    try:
        logger.info(f"Advice request: location={location}, message={message[:50]}...")
        
        # Validate inputs
        if not message or not message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        if not location or not location.strip():
            raise HTTPException(status_code=400, detail="Location cannot be empty")
        
        # Get chatbot response
        response = chatbot_response(message, location)
        
        # Add timestamp
        response["timestamp"] = datetime.now().isoformat()
        
        logger.info(f"Advice generated successfully for {location}")
        return response
    
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error in advice endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/advice", tags=["Chatbot"])
async def post_advice(request: AdviceRequest):
    """
    POST version of advice endpoint (accepts JSON body)
    """
    try:
        logger.info(f"POST Advice request: location={request.location}")
        
        response = chatbot_response(request.message, request.location)
        response["timestamp"] = datetime.now().isoformat()
        
        return response
    
    except Exception as e:
        logger.error(f"Error in POST advice endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analyze/{location}", tags=["Analysis"])
async def get_analysis(location: str):
    """
    Get comprehensive farm analysis without AI interpretation
    
    Returns raw analysis data:
    - Weather conditions
    - Soil properties
    - Market prices
    - Recommended crop (from decision engine)
    - Risk assessment
    - Profit estimates
    """
    try:
        logger.info(f"Analysis request for location: {location}")
        
        # Get farm analysis
        analysis = analyze_farm(location)
        analysis["timestamp"] = datetime.now().isoformat()
        
        logger.info(f"Analysis completed for {location}")
        return analysis
    
    except ValueError as e:
        logger.error(f"Location error: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error in analysis endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/weather/{location}", tags=["Data Services"])
async def get_weather_data(location: str):
    """
    Get current weather data for a location
    """
    try:
        logger.info(f"Weather request for: {location}")
        
        weather = get_weather(location)
        weather["location"] = location
        weather["timestamp"] = datetime.now().isoformat()
        
        return weather
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        logger.error(f"Weather API error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/soil/{location}", tags=["Data Services"])
async def get_soil_data(location: str):
    """
    Get soil data for a location
    """
    try:
        logger.info(f"Soil data request for: {location}")
        
        soil = get_soil(location)
        soil["timestamp"] = datetime.now().isoformat()
        
        return soil
    
    except Exception as e:
        logger.error(f"Soil data error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/price/{crop}", tags=["Data Services"])
async def get_crop_price(crop: str):
    """
    Get current market price for a crop
    """
    try:
        logger.info(f"Price request for crop: {crop}")
        
        price = get_price(crop)
        price["timestamp"] = datetime.now().isoformat()
        
        return price
    
    except Exception as e:
        logger.error(f"Price data error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/crops", tags=["Data Services"])
async def list_crops():
    """
    Get list of all available crops with current prices
    """
    try:
        logger.info("Listing all crops")
        
        crops = mandi_service.get_all_crops()
        crop_data = []
        
        for crop in crops:
            price_info = get_price(crop)
            crop_data.append({
                "name": crop,
                "price": price_info.get("current_price", price_info["price"]),
                "unit": price_info["unit"],
                "trend": price_info["trend"]
            })
        
        return {
            "total_crops": len(crop_data),
            "crops": crop_data,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error listing crops: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/compare-crops/{location}", tags=["Analysis"])
async def compare_crops(
    location: str,
    crops: str = Query(..., description="Comma-separated list of crops to compare"),
    area_acres: float = Query(1.0, description="Cultivation area in acres")
):
    """
    Compare profit potential of multiple crops for a location
    
    Example: /compare-crops/Pune?crops=wheat,rice,cotton&area_acres=2
    """
    try:
        logger.info(f"Crop comparison request: {crops} in {location}")
        
        crop_list = [c.strip() for c in crops.split(",")]
        
        if len(crop_list) < 2:
            raise HTTPException(
                status_code=400, 
                detail="Please provide at least 2 crops to compare"
            )
        
        comparison = mandi_service.compare_crops(crop_list, area_acres)
        
        return {
            "location": location,
            "area_acres": area_acres,
            "comparison": comparison,
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Comparison error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/quick-advice/{location}", tags=["Chatbot"])
async def quick_advice(location: str):
    """
    Get quick crop recommendation without custom query
    """
    try:
        logger.info(f"Quick advice request for: {location}")
        
        response = chatbot.get_quick_advice(location)
        response["timestamp"] = datetime.now().isoformat()
        
        return response
    
    except Exception as e:
        logger.error(f"Quick advice error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors
    """
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "An unexpected error occurred",
            "detail": str(exc)
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Run on application startup
    """
    logger.info("=" * 60)
    logger.info("Climate-Resilient Crop Advisory API Starting...")
    logger.info(f"Version: 1.0.0")
    logger.info(f"Debug Mode: {Config.DEBUG}")
    logger.info("=" * 60)
    
    # Validate configuration
    try:
        Config.validate()
        logger.info("✓ Configuration validated successfully")
    except ValueError as e:
        logger.warning(f"⚠ Configuration warning: {e}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Run on application shutdown
    """
    logger.info("Climate-Resilient Crop Advisory API Shutting Down...")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG,
        log_level="info"
    )
